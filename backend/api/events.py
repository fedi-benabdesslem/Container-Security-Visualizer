#!/usr/bin/env python3
# api/events.py - Event ingestion endpoint

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.event import Event
from backend.schemas.event import EventCreate, EventResponse
from backend.schemas.response import SuccessResponse
from backend.utils.logger import logger
from datetime import datetime
from backend.services.broadcast_manager import manager

router = APIRouter()


@router.post("/events", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
        event: EventCreate,
        db: Session = Depends(get_db)
):
    """
    Create a new event from collector

    This endpoint receives enriched events from the collector layer and stores them in the database.
    """
    try:
        # Convert ISO timestamp string to datetime
        timestamp_iso = datetime.fromisoformat(event.timestamp_iso.replace('Z', '+00:00'))

        # Create database model from schema
        db_event = Event(
            timestamp_ns=event.timestamp_ns,
            timestamp_iso=timestamp_iso,
            pid=event.pid,
            tgid=event.tgid,
            uid=event.uid,
            comm=event.comm,
            monitor_type=event.monitor_type,
            container_id=event.container_id,
            container_name=event.container_name,
            container_image=event.container_image,
            container_status=event.container_status,
            argv=event.argv,
            categories=event.categories,
            risk_score=event.risk_score,
            is_security_relevant=event.is_security_relevant,
            source_ip=event.source_ip,
            dest_ip=event.dest_ip,
            source_port=event.source_port,
            dest_port=event.dest_port,
            event_type=event.event_type,
            source_container_id=event.source_container_id,
            dest_container_id=event.dest_container_id,
            source_container_name=event.source_container_name,
            dest_container_name=event.dest_container_name
        )

        # Save to database
        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        logger.info(f"Event created: ID={db_event.id}, type={event.monitor_type}, pid={event.pid}")

        # Broadcast to WebSocket clients
        await manager.broadcast(db_event.to_dict())
        return SuccessResponse(
            message="Event created successfully",
            data={"event_id": db_event.id}
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create event: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )


@router.post("/events/batch", response_model=SuccessResponse)
async def create_events_batch(
        events: List[EventCreate],
        db: Session = Depends(get_db)
):
    """
    Create multiple events in a batch

    More efficient for high-volume ingestion
    """
    try:
        db_events = []

        for event in events:
            timestamp_iso = datetime.fromisoformat(event.timestamp_iso.replace('Z', '+00:00'))

            db_event = Event(
                timestamp_ns=event.timestamp_ns,
                timestamp_iso=timestamp_iso,
                pid=event.pid,
                tgid=event.tgid,
                uid=event.uid,
                comm=event.comm,
                monitor_type=event.monitor_type,
                container_id=event.container_id,
                container_name=event.container_name,
                container_image=event.container_image,
                container_status=event.container_status,
                argv=event.argv,
                categories=event.categories,
                risk_score=event.risk_score,
                is_security_relevant=event.is_security_relevant,
                source_ip=event.source_ip,
                dest_ip=event.dest_ip,
                source_port=event.source_port,
                dest_port=event.dest_port,
                event_type=event.event_type,
                source_container_id=event.source_container_id,
                dest_container_id=event.dest_container_id,
                source_container_name=event.source_container_name,
                dest_container_name=event.dest_container_name
            )
            db_events.append(db_event)

        # Bulk insert
        db.bulk_save_objects(db_events)
        db.commit()

        logger.info(f"Batch created: {len(db_events)} events")

        return SuccessResponse(
            message=f"Batch created successfully",
            data={"count": len(db_events)}
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create batch: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create batch: {str(e)}"
        )


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
        event_id: int,
        db: Session = Depends(get_db)
):
    """
    Get a specific event by ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found"
        )

    return event
