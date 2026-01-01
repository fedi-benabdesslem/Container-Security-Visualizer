#!/usr/bin/env python3
# api/query.py - Event query endpoints

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional

from backend.database import get_db
from backend.models.event import Event
from backend.schemas.event import EventResponse, EventListResponse
from backend.utils.logger import logger

router = APIRouter()


@router.get("/events", response_model=EventListResponse)
async def get_events(
        start_time: Optional[int] = Query(None, description="Start timestamp (nanoseconds)"),
        end_time: Optional[int] = Query(None, description="End timestamp (nanoseconds)"),
        monitor_type: Optional[str] = Query(None, description="Filter by monitor type"),
        container_id: Optional[str] = Query(None, description="Filter by container ID"),
        container_name: Optional[str] = Query(None, description="Filter by container name"),
        min_risk_score: Optional[int] = Query(None, ge=0, le=10, description="Minimum risk score"),
        search: Optional[str] = Query(None, description="Search in comm, container_name, argv"),
        limit: int = Query(50, ge=1, le=1000, description="Results per page"),
        offset: int = Query(0, ge=0, description="Pagination offset"),
        db: Session = Depends(get_db)
):
    """
    Query events with filters and pagination

    Returns a list of events matching the specified filters.
    """
    try:
        # Build query
        query = db.query(Event)

        # Apply filters
        filters = []

        if start_time is not None:
            filters.append(Event.timestamp_ns >= start_time)

        if end_time is not None:
            filters.append(Event.timestamp_ns <= end_time)

        if monitor_type:
            filters.append(Event.monitor_type == monitor_type)

        if container_id:
            filters.append(Event.container_id == container_id)

        if container_name:
            filters.append(Event.container_name == container_name)

        if min_risk_score is not None:
            filters.append(Event.risk_score >= min_risk_score)

        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Event.comm.ilike(search_pattern),
                    Event.container_name.ilike(search_pattern),
                    Event.argv.ilike(search_pattern)
                )
            )

        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))

        # Get total count before pagination
        total = query.count()

        # Apply ordering and pagination
        events = query.order_by(Event.timestamp_ns.desc()).offset(offset).limit(limit).all()

        # Calculate has_more
        has_more = (offset + limit) < total

        logger.info(f"Query returned {len(events)} events (total: {total}, offset: {offset})")

        return EventListResponse(
            events=events,
            total=total,
            limit=limit,
            offset=offset,
            has_more=has_more
        )

    except Exception as e:
        logger.error(f"Failed to query events: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query events: {str(e)}"
        )
