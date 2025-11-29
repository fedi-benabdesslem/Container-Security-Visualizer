#!/usr/bin/env python3
# Test configuration loading

from backend.config import config
from backend.utils.logger import logger


def test_config():
    logger.info("Testing configuration...")

    print(f"Server: {config.server.host}:{config.server.port}")
    print(f"Database URL: {config.database.url}")
    print(f"WebSocket max connections: {config.websocket.max_connections}")
    print(f"High risk threshold: {config.alerts.high_risk_threshold}")
    print(f"CORS origins: {config.cors.allow_origins}")

    logger.info("Configuration loaded successfully!")


if __name__ == "__main__":
    test_config()
