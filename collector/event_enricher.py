import sys
import os
import socket
import struct
from time import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities import (
    get_container_id_from_pid,
    get_container_metadata,
    get_all_container_ips,
    categorize_syscall,
    get_risk_score,
    is_security_relevant_syscall,
    config
)
class EventEnricher:
    def __init__(self):
        self.cache = {}
        self.ip_cache = {}
        self.ip_cache_time = 0
        self.pid_ttl = config.cache_ttl
        self.ip_ttl = 30
    def _int_to_ip(self, ip_int: int) -> str:
        if not ip_int:
            return None
        try:
            return socket.inet_ntoa(struct.pack('<I', ip_int))
        except Exception:
            return None
    def _refresh_ip_cache(self):
        now = time()
        if now - self.ip_cache_time >= self.ip_ttl:
            try:
                self.ip_cache = get_all_container_ips()
                self.ip_cache_time = now
            except Exception as e:
                print(f"Error refreshing IP cache: {e}", file=sys.stderr)
    def _get_container_id_from_ip(self, ip_addr: str) -> str:
        if not ip_addr:
            return None
        self._refresh_ip_cache()
        return self.ip_cache.get(ip_addr)
    def enrich(self, event: dict) -> dict:
        pid = event.get("pid")
        if pid is None:
            return None
        try:
            container_id = get_container_id_from_pid(int(pid))
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
        if container_id in self.cache:
            cached_metadata, cached_time = self.cache[container_id]
            if now - cached_time < self.pid_ttl:
                metadata = cached_metadata
            else:
                try:
                    metadata = get_container_metadata(container_id)
                    self.cache[container_id] = (metadata, now)
                except Exception as e:
                    print(f"Metadata error: {e}", file=sys.stderr)
                    metadata = cached_metadata
        else:
            try:
                metadata = get_container_metadata(container_id)
                self.cache[container_id] = (metadata, now)
            except Exception as e:
                print(f"Metadata error: {e}", file=sys.stderr)
                metadata = {}
        event["container_name"] = metadata.get("name") if metadata else None
        event["container_image"] = metadata.get("image") if metadata else None
        event["container_status"] = metadata.get("status") if metadata else None
        if event.get("monitor_type") == "syscall":
            syscall = event.get("syscall_name", "unknown")
            event["categories"] = categorize_syscall(syscall)
            event["risk_score"] = get_risk_score(syscall, event.get("uid"))
            event["is_security_relevant"] = is_security_relevant_syscall(syscall)
        elif event.get("monitor_type") == "network":
            saddr = event.get("saddr", 0)
            daddr = event.get("daddr", 0)
            event["source_ip"] = self._int_to_ip(saddr)
            event["dest_ip"] = self._int_to_ip(daddr)
            event["source_port"] = event.get("sport", 0)
            event["dest_port"] = event.get("dport", 0)
            event["event_type"] = "tcp_connect"
            dest_port = event.get("dest_port", 0)
            if dest_port in [22, 23, 3389]:
                event["risk_score"] = 5
                event["is_security_relevant"] = True
            elif dest_port in [80, 443, 8080, 8443]:
                event["risk_score"] = 1
                event["is_security_relevant"] = False
            else:
                event["risk_score"] = 3
                event["is_security_relevant"] = True
            event["categories"] = ["network"]
            source_container_id = container_id
            dest_ip = event.get("dest_ip")
            dest_container_id = self._get_container_id_from_ip(dest_ip)
            if source_container_id and dest_container_id:
                print(f"EDGE DETECTED: {source_container_id} -> {dest_container_id} (dest_ip: {dest_ip})", file=sys.stderr)
            if source_container_id:
                event["source_container_id"] = source_container_id
                if source_container_id in self.cache:
                    event["source_container_name"] = self.cache[source_container_id][0].get("name")
            if dest_container_id:
                event["dest_container_id"] = dest_container_id
                if dest_container_id in self.cache:
                    event["dest_container_name"] = self.cache[dest_container_id][0].get("name")
        return event