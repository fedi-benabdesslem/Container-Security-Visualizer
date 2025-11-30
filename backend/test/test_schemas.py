#!/usr/bin/env python3
# test_schemas.py - Test Pydantic schemas

from backend.schemas.event import EventCreate, EventResponse, EventFilter
from backend.schemas.response import SuccessResponse, StatsResponse
from backend.utils.logger import logger
from datetime import datetime


def test_schemas():
    """Test schema validation"""

    logger.info("Testing Pydantic schemas...")

    # Test 1: Valid syscall event
    try:
        syscall_event = EventCreate(
            timestamp_ns=1234567890123456789,
            timestamp_iso="2025-11-29T17:00:00Z",
            pid=12345,
            tgid=12345,
            uid=1000,
            comm="test_process",
            monitor_type="syscall",
            container_id="abc123456789",
            container_name="test_container",
            argv="/usr/bin/test",
            categories=["process", "security"],
            risk_score=5,
            is_security_relevant=True
        )
        logger.info(f"✅ Valid syscall event: {syscall_event.model_dump()}")
    except Exception as e:
        logger.error(f"❌ Syscall event validation failed: {e}")

    # Test 2: Valid network event
    try:
        network_event = EventCreate(
            timestamp_ns=1234567890123456790,
            timestamp_iso="2025-11-29T17:00:01Z",
            pid=12346,
            uid=1000,
            comm="curl",
            monitor_type="network",
            container_id="def987654321",
            container_name="web_container",
            source_ip="192.168.1.100",
            dest_ip="93.184.216.34",
            source_port=45678,
            dest_port=443,
            event_type="tcp_connect"
        )
        logger.info(f"✅ Valid network event: {network_event.model_dump()}")
    except Exception as e:
        logger.error(f"❌ Network event validation failed: {e}")

    # Test 3: Event filter
    try:
        event_filter = EventFilter(
            start_time=1234567890000000000,
            monitor_type="syscall",
            min_risk_score=7,
            limit=50
        )
        logger.info(f"✅ Valid filter: {event_filter.model_dump()}")
    except Exception as e:
        logger.error(f"❌ Filter validation failed: {e}")

    # Test 4: Invalid event (should fail)
    try:
        invalid_event = EventCreate(
            timestamp_ns="not_a_number",  # Invalid type
            timestamp_iso="2025-11-29T17:00:00Z",
            pid=12345,
            monitor_type="syscall"
        )
        logger.error("❌ Invalid event passed validation (should have failed!)")
    except Exception as e:
        logger.info(f"✅ Invalid event correctly rejected: {type(e).__name__}")

    # Test 5: Success response
    try:
        success = SuccessResponse(
            message="Event created successfully",
            data={"event_id": 123}
        )
        logger.info(f"✅ Success response: {success.model_dump()}")
    except Exception as e:
        logger.error(f"❌ Response validation failed: {e}")

    logger.info("Schema testing completed!")


if __name__ == "__main__":
    test_schemas()
