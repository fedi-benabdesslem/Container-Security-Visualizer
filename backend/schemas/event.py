#!/usr/bin/env python3
# schemas/event.py - Pydantic schemas for event validation

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class EventBase(BaseModel):
    """Base event schema with common fields"""
    timestamp_ns: int = Field(..., description="Nanosecond timestamp from kernel")
    timestamp_iso: str = Field(..., description="ISO 8601 timestamp")
    pid: int = Field(..., description="Process ID")
    tgid: Optional[int] = Field(None, description="Thread Group ID")
    uid: Optional[int] = Field(None, description="User ID")
    comm: Optional[str] = Field(None, description="Command/process name")
    monitor_type: str = Field(..., description="Event type: syscall or network")


class SyscallEventCreate(EventBase):
    """Schema for creating syscall events"""
    monitor_type: str = Field(default="syscall", description="Must be 'syscall'")

    # Container metadata
    container_id: Optional[str] = Field(None, max_length=12)
    container_name: Optional[str] = Field(None, max_length=255)
    container_image: Optional[str] = Field(None, max_length=255)
    container_status: Optional[str] = Field(None, max_length=20)

    # Syscall-specific
    argv: Optional[str] = Field(None, description="Command arguments")
    categories: Optional[List[str]] = Field(None, description="Syscall categories")
    risk_score: Optional[int] = Field(None, ge=0, le=10, description="Risk score 0-10")
    is_security_relevant: Optional[bool] = Field(None, description="Security relevance flag")


class NetworkEventCreate(EventBase):
    """Schema for creating network events"""
    monitor_type: str = Field(default="network", description="Must be 'network'")

    # Container metadata
    container_id: Optional[str] = Field(None, max_length=12)
    container_name: Optional[str] = Field(None, max_length=255)
    container_image: Optional[str] = Field(None, max_length=255)
    container_status: Optional[str] = Field(None, max_length=20)

    # Network-specific
    source_ip: Optional[str] = Field(None, max_length=45, description="Source IP address")
    dest_ip: Optional[str] = Field(None, max_length=45, description="Destination IP address")
    source_port: Optional[int] = Field(None, ge=0, le=65535, description="Source port")
    dest_port: Optional[int] = Field(None, ge=0, le=65535, description="Destination port")
    event_type: Optional[str] = Field(None, max_length=50, description="Event type (e.g., tcp_connect)")

    # Network enrichment
    source_container_id: Optional[str] = Field(None, max_length=12)
    dest_container_id: Optional[str] = Field(None, max_length=12)
    source_container_name: Optional[str] = Field(None, max_length=255)
    dest_container_name: Optional[str] = Field(None, max_length=255)


class EventCreate(BaseModel):
    """Generic event creation schema - accepts both syscall and network events"""
    timestamp_ns: int
    timestamp_iso: str
    pid: int
    tgid: Optional[int] = None
    uid: Optional[int] = None
    comm: Optional[str] = None
    monitor_type: str

    # Container metadata (common to both)
    container_id: Optional[str] = None
    container_name: Optional[str] = None
    container_image: Optional[str] = None
    container_status: Optional[str] = None

    # Syscall-specific (optional)
    argv: Optional[str] = None
    categories: Optional[List[str]] = None
    risk_score: Optional[int] = None
    is_security_relevant: Optional[bool] = None

    # Network-specific (optional)
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    source_port: Optional[int] = None
    dest_port: Optional[int] = None
    event_type: Optional[str] = None

    # Network enrichment
    source_container_id: Optional[str] = None
    dest_container_id: Optional[str] = None
    source_container_name: Optional[str] = None
    dest_container_name: Optional[str] = None


class EventResponse(EventCreate):
    """Schema for event responses - includes database fields"""
    id: int
    timestamp_iso: datetime
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None  # ← Auto-convert to ISO string
        }
    )


class EventFilter(BaseModel):
    """Schema for filtering events in queries"""
    start_time: Optional[int] = Field(None, description="Start timestamp (nanoseconds)")
    end_time: Optional[int] = Field(None, description="End timestamp (nanoseconds)")
    monitor_type: Optional[str] = Field(None, description="Filter by monitor type")
    container_id: Optional[str] = Field(None, description="Filter by container ID")
    container_name: Optional[str] = Field(None, description="Filter by container name")
    min_risk_score: Optional[int] = Field(None, ge=0, le=10, description="Minimum risk score")
    search: Optional[str] = Field(None, description="Search in comm, container_name, argv")
    limit: int = Field(50, ge=1, le=1000, description="Results per page")
    offset: int = Field(0, ge=0, description="Pagination offset")


class EventListResponse(BaseModel):
    """Schema for paginated event list response"""
    events: List[EventResponse]
    total: int
    limit: int
    offset: int
    has_more: bool
