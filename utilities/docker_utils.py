import os
import time
import sys
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
import json
import subprocess

def get_container_metadata(container_id: str) -> Dict[str, Optional[str]]:
    # Debug logging
    def log_debug(msg):
        try:
            with open("docker_utils_debug.log", "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
        except: pass

    log_debug(f"Getting metadata for {container_id}")
    # Try Docker SDK first with timeout
    try:
        # Some versions of docker-py have a bug with load_config()
        # We try to initialize it safely
        client = docker.from_env(timeout=5)
        container = client.containers.get(container_id)
        log_debug(f"SDK success: {container.name}")
        return {
            "name": container.name,
            "image": container.image.tags[0] if container.image.tags else str(container.image.id)[:12],
            "status": container.status
        }
    except (Exception, TypeError) as e:
        log_debug(f"SDK failed: {e}")
        # Fallback to subprocess if SDK fails
        try:
            log_debug(f"Trying subprocess fallback for {container_id}")
            cmd = ["docker", "inspect", container_id]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                data = json.loads(result.stdout)[0]
                name = data.get("Name", "").lstrip("/")
                image = data.get("Config", {}).get("Image", "")
                status = data.get("State", {}).get("Status", "")
                log_debug(f"Subprocess success: {name}")
                return {"name": name, "image": image, "status": status}
            else:
                log_debug(f"Subprocess failed with code {result.returncode}: {result.stderr}")
        except Exception as sub_e:
            log_debug(f"Error in metadata fallback: {sub_e}")
            
        return {"name": None, "image": None, "status": None}

def is_containerized(pid: int) -> bool:
    return get_container_id_from_pid(pid) is not None


def get_all_container_ips() -> Dict[str, str]:
    """
    Get a mapping of IP addresses to container IDs for all running containers.
    Returns a dict like {"172.17.0.2": "abc123def456", ...}
    """
    ip_to_container = {}
    
    # Try Docker SDK first with timeout
    try:
        # Some versions of docker-py have a bug with load_config()
        client = docker.from_env(timeout=5)
        for container in client.containers.list():
            try:
                # Get container's network settings
                networks = container.attrs.get("NetworkSettings", {}).get("Networks", {})
                container_id_short = container.id[:12]
                
                for net_name, net_info in networks.items():
                    ip_addr = net_info.get("IPAddress")
                    if ip_addr:
                        ip_to_container[ip_addr] = container_id_short
            except Exception:
                continue
    except (Exception, TypeError) as e:
        # Use stderr for collector logging
        print(f"Docker SDK failed for IPs, trying fallback: {e}", file=sys.stderr)
        # Fallback to subprocess
        try:
            cmd = ["docker", "ps", "-q"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                ids = result.stdout.strip().split()
                if ids:
                    inspect_cmd = ["docker", "inspect"] + ids
                    inspect_res = subprocess.run(inspect_cmd, capture_output=True, text=True, timeout=5)
                    if inspect_res.returncode == 0:
                        data = json.loads(inspect_res.stdout)
                        for container in data:
                            cid = container.get("Id", "")[:12]
                            networks = container.get("NetworkSettings", {}).get("Networks", {})
                            for net_name, net_info in networks.items():
                                ip = net_info.get("IPAddress")
                                if ip:
                                    ip_to_container[ip] = cid
                        print(f"IP Fallback success: mapped {len(ip_to_container)} IPs", file=sys.stderr)
            else:
                print(f"IP Fallback failed (docker ps): {result.stderr}", file=sys.stderr)
        except Exception as sub_e:
            print(f"Error in IP fallback: {sub_e}", file=sys.stderr)

    return ip_to_container