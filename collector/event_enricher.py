import sys
from time import time
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
        self.cache = {}  #cache PID->container mappings
        self.pid_ttl = config.cache_ttl
    def enrich(self, event: dict) -> dict:  #static method
        pid = event.get("pid")
        if pid is None:
            return None
        try:
            container_id = get_container_id_from_pid(int(pid))
        except Exception:
            container_id = None
        if container_id is None:
            return None
        event["container_id"] = container_id
        now = time()
        if container_id in self.cache:
            metadata, cached_time = self.cache[container_id]
            if now-cached_time < self.pid_ttl:
                pass
            else:
                try:
                    metadata = get_container_metadata(container_id)
                    self.cache[container_id] = metadata
                except Exception as e:
                    print(f"Metadata error: {e}", file=sys.stderr)
        else:
            try:
                metadata = get_container_metadata(container_id)
                self.cache[container_id] = metadata
            except Exception as e:
                print(f"Metadata error: {e}", file=sys.stderr)
        event["container_name"] = metadata.get("name")
        event["container_image"] = metadata.get("image")
        event["container_status"] = metadata.get("status")
        if event.get("monitor_type") == "syscall":
            syscall = event.get("syscall_name", "unknown")
            event["categories"] = categorize_syscall(syscall)
            event["risk_score"] = get_risk_score(syscall, event.get("uid"))
            event["is_security_relevant"] = is_security_relevant_syscall(syscall)
        return event