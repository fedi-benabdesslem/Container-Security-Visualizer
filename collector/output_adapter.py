#!/usr/bin/env python3
# output_adapter.py - Handles different output destinations

import json
import sys
import requests


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
            self.log_file = open(self.config.get("file_path", "events.log"), "a")

    def send(self, event: dict):
        """Send event to configured destination."""
        if self.mode == "stdout":
            print(json.dumps(event, ensure_ascii=False), flush=True)

        elif self.mode == "file":
            self.log_file.write(json.dumps(event) + "\n")
            self.log_file.flush()

        elif self.mode == "http":
            endpoint = self.config.get("api_endpoint", "http://localhost:8000/api/events")
            try:
                requests.post(endpoint, json=event, timeout=2)
            except Exception as e:
                print(f"HTTP POST error: {e}", file=sys.stderr)

    def close(self):
        """Clean up resources."""
        if self.mode == "file" and hasattr(self, 'log_file'):
            self.log_file.close()
