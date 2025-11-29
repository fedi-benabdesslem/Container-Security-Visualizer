#!/usr/bin/env python3
# schemas/response.py - Standard API response schemas

from pydantic import BaseModel
from typing import Optional, Any, Dict


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    version: str


class StatsResponse(BaseModel):
    """Statistics response"""
    total_events: int
    total_containers: int
    syscall_events: int
    network_events: int
    high_risk_events: int
    timespan_start: Optional[str] = None
    timespan_end: Optional[str] = None


class TimelineDataPoint(BaseModel):
    """Single data point for timeline"""
    timestamp: str
    count: int
    syscall_count: int = 0
    network_count: int = 0


class TimelineResponse(BaseModel):
    """Timeline data response"""
    interval: str  # "1m", "5m", "1h", etc.
    data: list[TimelineDataPoint]


class ContainerInfo(BaseModel):
    """Container information"""
    container_id: str
    container_name: str
    container_image: str
    event_count: int
    first_seen: str
    last_seen: str
    risk_level: str  # "low", "medium", "high"


class AlertEvent(BaseModel):
    """Alert event (high-risk event)"""
    id: int
    timestamp_iso: str
    container_name: Optional[str]
    comm: str
    risk_score: int
    categories: Optional[list[str]]
    description: str
