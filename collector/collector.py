import sys
import os
import subprocess
import threading
import queue
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from event_enricher import EventEnricher
from output_adapter import OutputAdapter
from utilities import config
EBPF_DIR = os.path.dirname(__file__)
SYSCALL_MONITOR = os.path.join(EBPF_DIR, config.ebpf_syscall_monitor)
NET_MONITOR = os.path.join(EBPF_DIR, config.ebpf_net_monitor)
event_queue = queue.Queue()
def read_monitor_output(process, monitor_type, event_queue):
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
    print("Starting collector...", file=sys.stderr, flush=True)
    print("Initializing EventEnricher...", file=sys.stderr, flush=True)
    enricher = EventEnricher()
    print("EventEnricher initialized.", file=sys.stderr, flush=True)
    output = OutputAdapter(mode=config.collector_output_mode, config={
        "api_endpoint": config.collector_api_endpoint
    })
    print(f"OutputAdapter initialized (mode: {config.collector_output_mode}).", file=sys.stderr, flush=True)
    sudo_cmd = []
    print(f"Starting syscall monitor (sudo: {os.geteuid() != 0})...", file=sys.stderr, flush=True)
    syscall_proc = subprocess.Popen(
        sudo_cmd + ["python3", SYSCALL_MONITOR],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1
    )
    print("Syscall monitor process started.", file=sys.stderr, flush=True)
    print(f"Starting network monitor (sudo: {os.geteuid() != 0})...", file=sys.stderr, flush=True)
    net_proc = subprocess.Popen(
        sudo_cmd + ["python3", NET_MONITOR],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1
    )
    print("Network monitor process started.", file=sys.stderr, flush=True)
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
    try:
        while True:
            try:
                event = event_queue.get(timeout=1)
                comm = event.get("comm", "unknown")
                argv = event.get("argv", "")
                mtype = event.get("monitor_type", "unknown")
                print(f"DEBUG: Processing {mtype} event: {comm} {argv}", file=sys.stderr)
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