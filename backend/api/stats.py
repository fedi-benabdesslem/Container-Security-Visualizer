from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import Optional
from datetime import datetime, timedelta
from backend.database import get_db
from backend.models.event import Event
from backend.schemas.response import StatsResponse, TimelineResponse, TimelineDataPoint
from backend.config import config
from backend.utils.logger import logger
router = APIRouter()
@router.get("/stats/summary", response_model=StatsResponse)
async def get_summary_stats(
        start_time: Optional[int] = Query(None, description="Start timestamp (nanoseconds)"),
        end_time: Optional[int] = Query(None, description="End timestamp (nanoseconds)"),
        db: Session = Depends(get_db)
):
    try:
        query = db.query(Event)
        if start_time:
            query = query.filter(Event.timestamp_ns >= start_time)
        if end_time:
            query = query.filter(Event.timestamp_ns <= end_time)
        total_events = query.count()
        total_containers = query.filter(Event.container_id.isnot(None)).with_entities(
            func.count(distinct(Event.container_id))
        ).scalar() or 0
        syscall_events = query.filter(Event.monitor_type == 'syscall').count()
        network_events = query.filter(Event.monitor_type == 'network').count()
        high_risk_threshold = config.alerts.high_risk_threshold
        high_risk_events = query.filter(Event.risk_score >= high_risk_threshold).count()
        timespan_query = query.with_entities(
            func.min(Event.timestamp_iso),
            func.max(Event.timestamp_iso)
        ).first()
        timespan_start = timespan_query[0].isoformat() if timespan_query[0] else None
        timespan_end = timespan_query[1].isoformat() if timespan_query[1] else None
        logger.info(f"Summary stats: total={total_events}, containers={total_containers}, high_risk={high_risk_events}")
        return StatsResponse(
            total_events=total_events,
            total_containers=total_containers,
            syscall_events=syscall_events,
            network_events=network_events,
            high_risk_events=high_risk_events,
            timespan_start=timespan_start,
            timespan_end=timespan_end
        )
    except Exception as e:
        logger.error(f"Failed to get summary stats: {e}", exc_info=True)
        raise
@router.get("/stats/timeline", response_model=TimelineResponse)
async def get_timeline(
        interval: str = Query("1m", description="Time interval: 1m, 5m, 15m, 1h"),
        start_time: Optional[int] = Query(None, description="Start timestamp (nanoseconds)"),
        end_time: Optional[int] = Query(None, description="End timestamp (nanoseconds)"),
        db: Session = Depends(get_db)
):
    try:
        interval_map = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "1h": 3600,
            "6h": 21600,
            "1d": 86400
        }
        interval_seconds = interval_map.get(interval, 60)
        query = db.query(Event)
        if start_time:
            query = query.filter(Event.timestamp_ns >= start_time)
        if end_time:
            query = query.filter(Event.timestamp_ns <= end_time)
        events = query.all()
        timeline_data = {}
        for event in events:
            timestamp = event.timestamp_iso
            interval_start = timestamp.replace(
                second=(timestamp.second // interval_seconds) * interval_seconds,
                microsecond=0
            )
            key = interval_start.isoformat()
            if key not in timeline_data:
                timeline_data[key] = {
                    "timestamp": key,
                    "count": 0,
                    "syscall_count": 0,
                    "network_count": 0
                }
            timeline_data[key]["count"] += 1
            if event.monitor_type == "syscall":
                timeline_data[key]["syscall_count"] += 1
            elif event.monitor_type == "network":
                timeline_data[key]["network_count"] += 1
        data_points = [TimelineDataPoint(**v) for v in timeline_data.values()]
        data_points.sort(key=lambda x: x.timestamp)
        logger.info(f"Timeline generated: {len(data_points)} data points, interval={interval}")
        return TimelineResponse(
            interval=interval,
            data=data_points
        )
    except Exception as e:
        logger.error(f"Failed to get timeline: {e}", exc_info=True)
        raise
