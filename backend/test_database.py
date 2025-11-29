#!/usr/bin/env python3
# test_database.py - Test database connection and models

from backend.database import init_db, drop_db, SessionLocal, engine
from backend.models.event import Event
from backend.utils.logger import logger
from datetime import datetime


def test_database():
    """Test database connection and basic operations"""

    logger.info("Testing database connection...")

    # Test 1: Initialize database
    try:
        init_db()
        logger.info("✅ Database initialization successful")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return

    # Test 2: Create a test event
    db = SessionLocal()
    try:
        test_event = Event(
            timestamp_ns=1234567890123456789,
            timestamp_iso=datetime.now(),
            pid=12345,
            tgid=12345,
            uid=1000,
            comm="test_process",
            monitor_type="syscall",
            container_id="abc123456789",
            container_name="test_container",
            container_image="nginx:latest",
            container_status="running",
            argv="/usr/bin/test",
            categories=["process", "security"],
            risk_score=5,
            is_security_relevant=True
        )

        db.add(test_event)
        db.commit()
        db.refresh(test_event)

        logger.info(f"✅ Test event created with ID: {test_event.id}")

        # Test 3: Query the event
        retrieved = db.query(Event).filter(Event.id == test_event.id).first()
        if retrieved:
            logger.info(f"✅ Event retrieved: {retrieved}")
            logger.info(f"   Event as dict: {retrieved.to_dict()}")
        else:
            logger.error("❌ Failed to retrieve event")

        # Test 4: Count total events
        count = db.query(Event).count()
        logger.info(f"✅ Total events in database: {count}")

    except Exception as e:
        logger.error(f"❌ Database operation failed: {e}")
        db.rollback()
    finally:
        db.close()

    logger.info("Database test completed!")


def cleanup_test_data():
    """Clean up test data"""
    logger.info("Cleaning up test data...")
    drop_db()
    logger.info("✅ Test data cleaned up")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        cleanup_test_data()
    else:
        test_database()
