#!/usr/bin/env python3
# api/containers.py - Container information endpoints

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from backend.database import get_db
from backend.models.event import Event
from backend.schemas.response import ContainerInfo
from backend.utils.logger import logger

router = APIRouter()


@router.get("/containers", response_model=List[ContainerInfo])
async def get_containers(
        db: Session = Depends(get_db)
):
    """
    Get list of all monitored containers

    Returns information about all containers that have generated events.
    """
    try:
        # Query containers with aggregated data
        container_data = db.query(
            Event.container_id,
            Event.container_name,
            Event.container_image,
            func.count(Event.id).label('event_count'),
            func.min(Event.timestamp_iso).label('first_seen'),
            func.max(Event.timestamp_iso).label('last_seen'),
            func.max(Event.risk_score).label('max_risk_score')
        ).filter(
            Event.container_id.isnot(None)
        ).group_by(
            Event.container_id,
            Event.container_name,
            Event.container_image
        ).all()

        containers = []
        for data in container_data:
            # Determine risk level
            max_risk = data.max_risk_score or 0
            if max_risk >= 7:
                risk_level = "high"
            elif max_risk >= 4:
                risk_level = "medium"
            else:
                risk_level = "low"

            containers.append(ContainerInfo(
                container_id=data.container_id,
                container_name=data.container_name or "unknown",
                container_image=data.container_image or "unknown",
                event_count=data.event_count,
                first_seen=data.first_seen.isoformat(),
                last_seen=data.last_seen.isoformat(),
                risk_level=risk_level
            ))

        # Sort by last_seen (most recent first)
        containers.sort(key=lambda x: x.last_seen, reverse=True)

        logger.info(f"Containers retrieved: {len(containers)}")

        return containers

    except Exception as e:
        logger.error(f"Failed to get containers: {e}", exc_info=True)
        raise


@router.get("/containers/{container_id}/events")
async def get_container_events(
        container_id: str,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """
    Get events for a specific container
    """
    events = db.query(Event).filter(
        Event.container_id == container_id
    ).order_by(
        Event.timestamp_ns.desc()
    ).limit(limit).all()

    return {"events": [event.to_dict() for event in events]}
