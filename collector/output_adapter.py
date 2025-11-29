#!/usr/bin/env python3
# output_adapter.py - Handles different output destinations

import json
import sys
import requests
from datetime import datetime


class OutputAdapter:
    """Abstraction for sending enriched events to different destinations."""

    def __init__(self, mode="stdout", config=None):
        """
        mode: "stdout", "file", or "http"
        config: dict with settings (file_path, api_endpoint, etc.)
        """
        self.mode = mode
        self.config = config or {}

        if mode == "file":
            file_path = self.config.get("file_path", "events.log")
            self.log_file = open(file_path, "a")

        if mode == "http":
            self.api_endpoint = self.config.get("api_endpoint", "http://localhost:8000/api/events")
            self.session = requests.Session()
            self.session.headers.update({"Content-Type": "application/json"})
            print(f"HTTP mode: Sending events to {self.api_endpoint}", file=sys.stderr)

    def send(self, event: dict):
        """Send event to configured destination."""
        if self.mode == "stdout":
            print(json.dumps(event, ensure_ascii=False), flush=True)

        elif self.mode == "file":
            self.log_file.write(json.dumps(event) + "\n")
            self.log_file.flush()

        elif self.mode == "http":
            try:
                response = self.session.post(
                    self.api_endpoint,
                    json=event,
                    timeout=5
                )

                if response.status_code == 201:
                    # Successfully created
                    result = response.json()
                    event_id = result.get("data", {}).get("event_id")
                    print(f"✓ Event sent (ID: {event_id})", file=sys.stderr)
                else:
                    print(f"✗ Failed to send event: {response.status_code} - {response.text}", file=sys.stderr)

            except requests.exceptions.Timeout:
                print(f"✗ Timeout sending event to backend", file=sys.stderr)
            except requests.exceptions.ConnectionError:
                print(f"✗ Connection error: Backend not reachable at {self.api_endpoint}", file=sys.stderr)
            except Exception as e:
                print(f"✗ HTTP POST error: {e}", file=sys.stderr)

    def close(self):
        """Clean up resources."""
        if self.mode == "file" and hasattr(self, 'log_file'):
            self.log_file.close()

        if self.mode == "http" and hasattr(self, 'session'):
            self.session.close()
