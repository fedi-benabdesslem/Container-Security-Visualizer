import os
import docker
import docker.errors
from typing import Optional, Dict
def get_container_id_from_pid(pid: int) -> Optional[str]:
    cgroup_file = f"/proc/{pid}/cgroup"
    if not os.path.exists(cgroup_file):
        return None
    try:
        with open(cgroup_file, "r") as fh:
            lines = fh.readlines()
            # Debug logging
            try:
                with open("/tmp/cgroup_debug.log", "a") as log:
                    log.write(f"PID {pid} cgroup: {lines}\n")
            except: pass

            for line in lines:
                parts = line.strip().split(":")
                if len(parts) < 3:
                    continue
                path = parts[2]
                
                # Handle cgroup v2 paths like .../docker-<id>.scope
                tokens = path.split("/")
                for t in reversed(tokens):
                    # Handle systemd scope naming
                    if t.endswith(".scope"):
                        t = t[:-6]
                    if t.startswith("docker-"):
                        t = t[7:]
                    
                    # Check for container ID format (hex string >= 12 chars)
                    # Docker IDs are 64-char hex, we take first 12
                    if len(t) >= 12 and all(c in '0123456789abcdefABCDEF' for c in t):
                        try:
                            with open("/tmp/cgroup_debug.log", "a") as log:
                                log.write(f"  MATCH: {t[:12]}\n")
                        except: pass
                        return t[:12]
    except Exception:
        return None
    return None
def get_container_metadata(container_id: str) -> Dict[str, Optional[str]]:
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        return {
            "name": container.name,
            "image": container.image.tags[0] if container.image.tags else str(container.image.id)[:12],
            "status": container.status
        }
    except docker.errors.NotFound:
        return {"name": None, "image": None, "status": None}
    except docker.errors.APIError as e:
        print(f"Docker API error: {e}")
        return {"name": None, "image": None, "status": None}
    except Exception as e:
        print(f"Error accessing Docker: {e}")
        return {"name": None, "image": None, "status": None}
def is_containerized(pid: int) -> bool:
    return get_container_id_from_pid(pid) is not None