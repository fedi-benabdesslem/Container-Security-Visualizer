#!/usr/bin/env python3
# api/websocket.py - WebSocket endpoints

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional

from backend.services.broadcast_manager import manager
from backend.utils.logger import logger

router = APIRouter()


@router.websocket("/events")
async def websocket_endpoint(
        websocket: WebSocket,
        monitor_type: Optional[str] = Query(None, description="Filter by monitor type"),
        container_id: Optional[str] = Query(None, description="Filter by container ID"),
        min_risk_score: Optional[int] = Query(None, description="Minimum risk score"),
        suspicious_only: Optional[bool] = Query(False, description="Only security-relevant events"),
):
    """
    WebSocket endpoint for real-time event streaming

    Connect to this endpoint to receive events in real-time.
    Supports optional filters via query parameters.

    Example: ws://localhost:8000/ws/events?monitor_type=syscall&min_risk_score=5
    """
    # Build filters from query parameters
    filters = {}
    if monitor_type:
        filters["monitor_type"] = monitor_type
    if container_id:
        filters["container_id"] = container_id
    if min_risk_score is not None:
        filters["min_risk_score"] = min_risk_score
    if suspicious_only:
        filters["suspicious_only"] = True

    # Accept connection
    await manager.connect(websocket, filters)

    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connected",
            "message": "Connected to event stream",
            "filters": filters,
            "active_connections": manager.get_connection_count()
        }, websocket)

        # Keep connection alive and listen for client messages
        while True:
            # Receive messages from client (e.g., filter updates, ping)
            data = await websocket.receive_text()

            # Handle client messages
            if data == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)
            elif data == "stats":
                await manager.send_personal_message({
                    "type": "stats",
                    "active_connections": manager.get_connection_count()
                }, websocket)

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)


@router.get("/connections")
async def get_connection_stats():
    """Get WebSocket connection statistics"""
    return {
        "active_connections": manager.get_connection_count()
    }
