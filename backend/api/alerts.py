from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.event import Event
from backend.schemas.response import AlertEvent
from backend.config import config
from backend.utils.logger import logger
router = APIRouter()
@router.get("/alerts", response_model=List[AlertEvent])
async def get_alerts(
        limit: int = Query(50, ge=1, le=500, description="Maximum number of alerts"),
        db: Session = Depends(get_db)
):
    try:
        threshold = config.alerts.high_risk_threshold
        events = db.query(Event).filter(
            Event.risk_score >= threshold
        ).order_by(
            Event.timestamp_ns.desc()
        ).limit(limit).all()
        alerts = []
        for event in events:
            description = f"{event.comm or 'Unknown process'} (PID: {event.pid})"
            if event.container_name:
                description += f" in container {event.container_name}"
            if event.argv:
                description += f": {event.argv}"
            alerts.append(AlertEvent(
                id=event.id,
                timestamp_iso=event.timestamp_iso.isoformat(),
                container_name=event.container_name,
                comm=event.comm or "unknown",
                risk_score=event.risk_score or 0,
                categories=event.categories,
                description=description
            ))
        logger.info(f"Alerts retrieved: {len(alerts)} high-risk events")
        return alerts
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}", exc_info=True)
        raise
