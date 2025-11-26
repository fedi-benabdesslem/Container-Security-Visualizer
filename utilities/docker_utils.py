#!/usr/bin/env python3
# docker_utils.py
# PID -> container ID mapping and container metadata retrieval

import os
import docker
import docker.errors
from typing import Optional, Dict


def get_container_id_from_pid(pid: int) -> Optional[str]:
    """
    Attempts to extract a docker container id from /proc/<pid>/cgroup.
    Returns short container id (12 chars) or None if not found.
    """
    cgroup_file = f"/proc/{pid}/cgroup"
    if not os.path.exists(cgroup_file):
        return None

    try:
        with open(cgroup_file, "r") as fh:
            for line in fh:
                # Typical docker line contains ".../docker/<containerid>"
                parts = line.strip().split(":")
                if len(parts) < 3:
                    continue
                path = parts[2]

                # Look for long hash-like tokens in the path
                tokens = path.split("/")
                for t in reversed(tokens):
                    # Container IDs are typically 64 hex chars, we want first 12
                    if len(t) >= 12 and all(c.isalnum() or c == '-' for c in t):
                        # Return first 12 chars of container ID
                        return t[:12]
    except Exception:
        return None

    return None


def get_container_metadata(container_id: str) -> Dict[str, Optional[str]]:
    """
    Get container metadata (name, image, status) using Docker SDK.
    Returns dict with name, image, and status, or None values if not found.
    """
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)

        return {
            "name": container.name,
            "image": container.image.tags[0] if container.image.tags else str(container.image.id)[:12],
            "status": container.status
        }
    except docker.errors.NotFound:
        # Container not found
        return {"name": None, "image": None, "status": None}
    except docker.errors.APIError as e:
        # Docker API error
        print(f"Docker API error: {e}")
        return {"name": None, "image": None, "status": None}
    except Exception as e:
        # Other errors (Docker not running, permissions, etc.)
        print(f"Error accessing Docker: {e}")
        return {"name": None, "image": None, "status": None}


def is_containerized(pid: int) -> bool:
    """
    Quick check if a PID belongs to a containerized process.
    Returns True if container ID found, False otherwise.
    """
    return get_container_id_from_pid(pid) is not None
