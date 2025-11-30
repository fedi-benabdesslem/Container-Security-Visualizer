#!/usr/bin/env python3
# collector.py - Main orchestrator that launches monitors and coordinates enrichment

import sys
import os
import subprocess
import threading
import queue

# Add common to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utilities'))

from event_enricher import EventEnricher
from output_adapter import OutputAdapter

# Paths to monitor scripts
EBPF_DIR = os.path.join(os.path.dirname(__file__), "..", "ebpf")
SYSCALL_MONITOR = os.path.join(EBPF_DIR, "syscall_monitor.py")
NET_MONITOR = os.path.join(EBPF_DIR, "net_monitor.py")

event_queue = queue.Queue()


def read_monitor_output(process, monitor_type, event_queue):
    """Read JSON lines from monitor subprocess and queue them."""
    try:
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if not line or not line.startswith('{'):
                if line:
                    print(f"[{monitor_type}] {line}", file=sys.stderr)
                continue

            try:
                import json
                event = json.loads(line)
                event["monitor_type"] = monitor_type
                event_queue.put(event)
            except json.JSONDecodeError as e:
                print(f"[{monitor_type}] JSON error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"[{monitor_type}] Error: {e}", file=sys.stderr)


def main():
    print("Starting collector...", file=sys.stderr)

    # Initialize enricher and output adapter
    enricher = EventEnricher()
    output = OutputAdapter(mode="http", config={
        "api_endpoint": "http://localhost:8000/api/events"
    })

    # Launch monitors
    syscall_proc = subprocess.Popen(
        ["sudo", "python3", SYSCALL_MONITOR],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1
    )

    net_proc = subprocess.Popen(
        ["sudo", "python3", NET_MONITOR],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1
    )

    # Start reader threads
    threading.Thread(
        target=read_monitor_output,
        args=(syscall_proc, "syscall", event_queue),
        daemon=True
    ).start()

    threading.Thread(
        target=read_monitor_output,
        args=(net_proc, "network", event_queue),
        daemon=True
    ).start()

    print("Collector ready...", file=sys.stderr)

    # Main event loop
    try:
        while True:
            try:
                event = event_queue.get(timeout=1)
                enriched = enricher.enrich(event)
                if enriched is None:
                    continue
                output.send(enriched)
            except queue.Empty:
                if syscall_proc.poll() is not None or net_proc.poll() is not None:
                    break
                continue
    except KeyboardInterrupt:
        print("\nStopping collector...", file=sys.stderr)
    finally:
        syscall_proc.terminate()
        net_proc.terminate()
        syscall_proc.wait()
        net_proc.wait()


if __name__ == "__main__":
    main()
