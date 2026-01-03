from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.analytics import analytics
from backend.utils.logger import logger
router = APIRouter()
@router.get("/analytics/distribution")
async def get_distribution(db: Session = Depends(get_db)):
    return analytics.get_event_distribution_by_type(db)
@router.get("/analytics/risk-distribution")
async def get_risk_dist(db: Session = Depends(get_db)):
    return analytics.get_risk_distribution(db)
@router.get("/analytics/top-containers")
async def get_top_containers(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    results = analytics.get_top_containers_by_event_count(db, limit)
    return {
        "containers": [
            {"container_id": c[0], "container_name": c[1], "event_count": c[2]}
            for c in results
        ]
    }
@router.get("/analytics/top-processes")
async def get_top_processes(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    results = analytics.get_top_processes_by_event_count(db, limit)
    return {
        "processes": [
            {"process": p[0], "event_count": p[1]}
            for p in results
        ]
    }
@router.get("/analytics/risky-containers")
async def get_risky_containers(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return {"containers": analytics.get_most_risky_containers(db, limit)}
@router.get("/analytics/network-summary")
async def get_network_summary(db: Session = Depends(get_db)):
    return analytics.get_network_connections_summary(db)
@router.get("/analytics/anomalies")
async def detect_anomalies(db: Session = Depends(get_db)):
    return {"anomalies": analytics.detect_anomalies(db)}
