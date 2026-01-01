#!/usr/bin/env python3
# services/event_processor.py - Business logic for event processing

from typing import Dict, Optional
from datetime import datetime
from backend.utils.logger import logger


class EventProcessor:
    """
    Processes and validates events before storage
    Can add additional enrichment or transformation logic here
    """

    def __init__(self):
        self.processed_count = 0
        self.error_count = 0

    def validate_event(self, event: Dict) -> bool:
        """
        Validate that event has required fields and valid values

        Returns True if valid, False otherwise
        """
        required_fields = ["timestamp_ns", "timestamp_iso", "pid", "monitor_type"]

        # Check required fields
        for field in required_fields:
            if field not in event:
                logger.warning(f"Event missing required field: {field}")
                return False

        # Validate monitor_type
        if event["monitor_type"] not in ["syscall", "network"]:
            logger.warning(f"Invalid monitor_type: {event['monitor_type']}")
            return False

        # Validate pid
        if not isinstance(event["pid"], int) or event["pid"] <= 0:
            logger.warning(f"Invalid PID: {event['pid']}")
            return False

        # Validate timestamp
        if not isinstance(event["timestamp_ns"], int):
            logger.warning(f"Invalid timestamp_ns: {event['timestamp_ns']}")
            return False

        # Validate risk_score if present
        if "risk_score" in event and event["risk_score"] is not None:
            if not isinstance(event["risk_score"], int) or not (0 <= event["risk_score"] <= 10):
                logger.warning(f"Invalid risk_score: {event['risk_score']}")
                return False

        return True

    def enrich_event(self, event: Dict) -> Dict:
        """
        Add additional enrichment to event
        This is called after initial enrichment from collector
        """
        # Add processing timestamp
        event["processed_at"] = datetime.utcnow().isoformat()

        # Normalize container_id (ensure it's 12 chars if present)
        if event.get("container_id") and len(event["container_id"]) > 12:
            event["container_id"] = event["container_id"][:12]

        # Add event severity based on risk_score
        risk_score = event.get("risk_score", 0)
        if risk_score is not None:
            if risk_score >= 8:
                event["severity"] = "critical"
            elif risk_score >= 6:
                event["severity"] = "high"
            elif risk_score >= 4:
                event["severity"] = "medium"
            else:
                event["severity"] = "low"
        else:
            event["severity"] = "unknown"

        return event

    def process_event(self, event: Dict) -> Optional[Dict]:
        """
        Main processing function - validates and enriches event

        Returns processed event or None if invalid
        """
        try:
            # Validate
            if not self.validate_event(event):
                self.error_count += 1
                return None

            # Enrich
            processed_event = self.enrich_event(event)

            self.processed_count += 1

            return processed_event

        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)
            self.error_count += 1
            return None

    def get_stats(self) -> Dict:
        """Get processing statistics"""
        return {
            "processed": self.processed_count,
            "errors": self.error_count,
            "success_rate": (
                self.processed_count / (self.processed_count + self.error_count) * 100
                if (self.processed_count + self.error_count) > 0
                else 0
            )
        }

    def reset_stats(self):
        """Reset processing statistics"""
        self.processed_count = 0
        self.error_count = 0


# Global processor instance
processor = EventProcessor()
