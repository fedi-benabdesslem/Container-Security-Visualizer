#!/usr/bin/env python3
# services/broadcast_manager.py - WebSocket connection manager

from fastapi import WebSocket
from typing import List, Set, Dict, Optional
import asyncio
import json
from backend.utils.logger import logger


class ConnectionManager:
    """Manages WebSocket connections and broadcasts events"""

    def __init__(self):
        # Store active connections with their filters
        self.active_connections: Dict[WebSocket, Dict] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, filters: Optional[Dict] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        async with self._lock:
            self.active_connections[websocket] = filters or {}
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        async with self._lock:
            if websocket in self.active_connections:
                del self.active_connections[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    def _event_matches_filter(self, event: dict, filters: Dict) -> bool:
        """Check if event matches connection's filters"""
        if not filters:
            return True

        # Filter by monitor_type
        if "monitor_type" in filters:
            if event.get("monitor_type") != filters["monitor_type"]:
                return False

        # Filter by container_id
        if "container_id" in filters:
            if event.get("container_id") != filters["container_id"]:
                return False

        # Filter by min_risk_score
        if "min_risk_score" in filters:
            risk_score = event.get("risk_score", 0)
            if risk_score is None or risk_score < filters["min_risk_score"]:
                return False

        # Filter for suspicious only
        if filters.get("suspicious_only"):
            if not event.get("is_security_relevant"):
                return False

        return True

    async def broadcast(self, event: dict):
        """
        Broadcast event to all connected clients
        Respects per-connection filters
        """
        if not self.active_connections:
            return

        disconnected = []

        async with self._lock:
            connections = list(self.active_connections.items())

        for websocket, filters in connections:
            # Check if event matches this connection's filters
            if not self._event_matches_filter(event, filters):
                continue

            try:
                await websocket.send_json(event)
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                disconnected.append(websocket)

        # Clean up disconnected clients
        if disconnected:
            async with self._lock:
                for ws in disconnected:
                    if ws in self.active_connections:
                        del self.active_connections[ws]
            logger.info(f"Cleaned up {len(disconnected)} disconnected clients")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")

    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()
