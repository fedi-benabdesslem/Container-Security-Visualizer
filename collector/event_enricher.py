#!/usr/bin/env python3
# event_enricher.py - Enriches events with container metadata

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utilities.docker_utils import get_container_id_from_pid, get_container_metadata
from utilities.syscall_utils import categorize_syscall, get_risk_score, is_security_relevant_syscall


class EventEnricher:
    """Enriches raw events with container metadata."""

    def __init__(self):
        self.cache = {}  # Optional: cache PID->container mappings
#static method: does not use self. belongs to class, but does not modify class state.
    def enrich(self, event: dict) -> dict:
        """Add container metadata to event based on PID."""
        pid = event.get("pid")

        if pid is None:
            event["container_id"] = None
            event["container_name"] = None
            event["container_image"] = None
            return event

        # Get container ID
        try:
            container_id = get_container_id_from_pid(int(pid))
        except Exception:
            container_id = None

        event["container_id"] = container_id

        # Get full metadata if container found
        if container_id:
            try:
                metadata = get_container_metadata(container_id)
                event["container_name"] = metadata.get("name")
                event["container_image"] = metadata.get("image")
                event["container_status"] = metadata.get("status")
                if event.get("monitor_type") == "syscall":
                    syscall = "execve"
                    event["categories"] = categorize_syscall(syscall)
                    event["risk_score"] = get_risk_score(syscall, event.get("uid"))
                    event["is_security_relevant"] = is_security_relevant_syscall(syscall)
            except Exception as e:
                print(f"Metadata error: {e}", file=sys.stderr)
                event["container_name"] = None
                event["container_image"] = None
                event["container_status"] = None
        else:
            event["container_name"] = None
            event["container_image"] = None
            event["container_status"] = None

        return event
