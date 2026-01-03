from pydantic import BaseModel
from typing import Optional, Any, Dict
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
class HealthResponse(BaseModel):
    status: str
    database: str
    version: str
class StatsResponse(BaseModel):
    total_events: int
    total_containers: int
    syscall_events: int
    network_events: int
    high_risk_events: int
    timespan_start: Optional[str] = None
    timespan_end: Optional[str] = None
class TimelineDataPoint(BaseModel):
    timestamp: str
    count: int
    syscall_count: int = 0
    network_count: int = 0
class TimelineResponse(BaseModel):
    interval: str
    data: list[TimelineDataPoint]
class ContainerInfo(BaseModel):
    container_id: str
    container_name: str
    container_image: str
    event_count: int
    first_seen: str
    last_seen: str
    risk_level: str
class AlertEvent(BaseModel):
    id: int
    timestamp_iso: str
    container_name: Optional[str]
    comm: str
    risk_score: int
    categories: Optional[list[str]]
    description: str
