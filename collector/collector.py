import sys
import os
import subprocess
import threading
import queue
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
    print("Starting collector...", file=sys.stderr)
    enricher = EventEnricher()
    output = OutputAdapter(mode=config.collector_output_mode, config={
        "api_endpoint": config.collector_api_endpoint
    })
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
    try:    # Main
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