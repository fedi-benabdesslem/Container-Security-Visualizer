import sys
import os
import socket
import struct
from time import time

# Add parent directory to path so utilities can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities import (
    get_container_id_from_pid,
    get_container_metadata,
    categorize_syscall,
    get_risk_score,
    is_security_relevant_syscall,
    config
)


class EventEnricher:
    def __init__(self):
        self.cache = {}  # cache container_id -> (metadata, cached_time)
        self.pid_ttl = config.cache_ttl

    def _int_to_ip(self, ip_int: int) -> str:
        """Convert integer IP address to dotted string notation."""
        if not ip_int:
            return None
        try:
            # Network byte order (little-endian on x86)
            return socket.inet_ntoa(struct.pack('<I', ip_int))
        except Exception:
            return None

    def enrich(self, event: dict) -> dict:
        """Enrich event with container metadata and additional fields."""
        pid = event.get("pid")
        if pid is None:
            return None

        try:
            container_id = get_container_id_from_pid(int(pid))
            # Debug logging
            try:
                with open("/tmp/enricher_debug.log", "a") as log:
                    log.write(f"PID {pid} -> Container ID: {container_id}\n")
            except: pass
        except Exception as e:
            try:
                with open("/tmp/enricher_debug.log", "a") as log:
                    log.write(f"Error mapping PID {pid}: {e}\n")
            except: pass
            container_id = None

        if container_id is None:
            return None

        event["container_id"] = container_id
        now = time()
        metadata = None

        # Check cache for container metadata
        if container_id in self.cache:
            cached_metadata, cached_time = self.cache[container_id]
            if now - cached_time < self.pid_ttl:
                # Cache is still valid
                metadata = cached_metadata
            else:
                # Cache expired, refresh
                try:
                    metadata = get_container_metadata(container_id)
                    self.cache[container_id] = (metadata, now)
                except Exception as e:
                    print(f"Metadata error: {e}", file=sys.stderr)
                    metadata = cached_metadata  # Fall back to cached data
        else:
            # Not in cache, fetch and store
            try:
                metadata = get_container_metadata(container_id)
                self.cache[container_id] = (metadata, now)
            except Exception as e:
                print(f"Metadata error: {e}", file=sys.stderr)
                metadata = {}

        # Apply container metadata
        event["container_name"] = metadata.get("name") if metadata else None
        event["container_image"] = metadata.get("image") if metadata else None
        event["container_status"] = metadata.get("status") if metadata else None

        # Enrich based on monitor type
        if event.get("monitor_type") == "syscall":
            syscall = event.get("syscall_name", "unknown")
            event["categories"] = categorize_syscall(syscall)
            event["risk_score"] = get_risk_score(syscall, event.get("uid"))
            event["is_security_relevant"] = is_security_relevant_syscall(syscall)

        elif event.get("monitor_type") == "network":
            # Convert integer IP addresses to string format
            saddr = event.get("saddr", 0)
            daddr = event.get("daddr", 0)
            event["source_ip"] = self._int_to_ip(saddr)
            event["dest_ip"] = self._int_to_ip(daddr)

            # Normalize port field names (sport/dport -> source_port/dest_port)
            event["source_port"] = event.get("sport", 0)
            event["dest_port"] = event.get("dport", 0)

            # Add event type
            event["event_type"] = "tcp_connect"

            # Basic risk scoring for network events
            dest_port = event.get("dest_port", 0)
            # Higher risk for connections to well-known ports or unusual ports
            if dest_port in [22, 23, 3389]:  # SSH, Telnet, RDP
                event["risk_score"] = 5
                event["is_security_relevant"] = True
            elif dest_port in [80, 443, 8080, 8443]:  # HTTP/HTTPS
                event["risk_score"] = 1
                event["is_security_relevant"] = False
            else:
                event["risk_score"] = 3
                event["is_security_relevant"] = True

            event["categories"] = ["network"]

        return event