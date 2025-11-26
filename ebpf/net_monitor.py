#!/usr/bin/env python3
# BCC-based loader for net_monitor.c — monitors TCP connection events
# Captures source/dest IPs, ports, and process metadata
# Run as root.

from bcc import BPF
from datetime import datetime
import json
import os
import signal
import sys
import socket
import struct

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
C_FILE = os.path.join(THIS_DIR, "net_monitor.c")

# Load BPF program with tracepoint attachment
b = BPF(src_file=C_FILE)

# Attach kprobe to tcp_v4_connect for outgoing connections
b.attach_kprobe(event="tcp_v4_connect", fn_name="trace_connect")

print("Loaded BPF network monitor. Listening for TCP connections... (CTRL-C to exit)")


def _bytes_to_str(b):
    """Convert bytes to string, handling null termination"""
    if not b:
        return ""
    try:
        return b.decode('utf-8', 'ignore').rstrip("\x00")
    except Exception:
        return str(b)


def _ip_to_str(ip_int):
    """Convert 32-bit integer IP to dotted decimal string"""
    try:
        # IP is stored in network byte order (big-endian)
        return socket.inet_ntoa(struct.pack("I", ip_int))
    except Exception:
        return str(ip_int)


def handle_net_event(cpu, data, size):
    """Process network events from perf buffer"""
    evt = b["net_events"].event(data)

    out = {
        "timestamp_ns": int(evt.ts_ns),
        "timestamp_iso": datetime.fromtimestamp(evt.ts_ns / 1e9).isoformat() + "Z",
        "pid": int(evt.pid),
        "tgid": int(evt.tgid),
        "uid": int(evt.uid),
        "comm": _bytes_to_str(evt.comm),
        "source_ip": _ip_to_str(evt.saddr),
        "dest_ip": _ip_to_str(evt.daddr),
        "source_port": int(evt.sport),
        "dest_port": int(evt.dport),
        "ip_version": int(evt.ip_version),
        "event_type": "tcp_connect"
    }

    print(json.dumps(out, ensure_ascii=False))


# Open perf buffer for network events
b["net_events"].open_perf_buffer(handle_net_event)


def exit_gracefully(signum, frame):
    print("\nDetaching network monitor and exiting.")
    sys.exit(0)


signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)

# Main event loop
while True:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit_gracefully(None, None)
