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
            for line in fh:
                parts = line.strip().split(":")
                if len(parts) < 3:
                    continue
                path = parts[2]
                tokens = path.split("/")
                for t in reversed(tokens):
                    if len(t) >= 12 and all(c.isalnum() or c == '-' for c in t):
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