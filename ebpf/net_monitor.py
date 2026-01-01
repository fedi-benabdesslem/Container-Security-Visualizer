from bcc import BPF
from datetime import datetime
import json
import os
import signal
import sys

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
C_FILE = os.path.join(THIS_DIR, "net_monitor.c")  # ensure name matches

b = BPF(src_file=C_FILE)
b.attach_tracepoint(tp="syscalls:sys_enter_connect", fn_name="trace_connect")
# b.attach_tracepoint(tp="syscalls:sys_enter_connect", fn_name="trace_connect")

print("Loaded BPF program and attached to sys_enter_connect tracepoint. Listening for events... (CTRL-C to exit)", flush=True)

def _bytes_to_str(bv):
    if not bv:
        return ""
    try:
        return bv.decode("utf-8", "ignore").rstrip("\x00")
    except Exception:
        return str(bv)

# Calculate boot time offset to convert monotonic time to epoch time
def get_boot_time():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        return datetime.now().timestamp() - uptime_seconds

BOOT_TIME_OFFSET = get_boot_time()

def handle_event(cpu, data, size):
    evt = b["net_events"].event(data)
    # Convert monotonic ns to epoch seconds
    timestamp_seconds = BOOT_TIME_OFFSET + (evt.ts_ns / 1e9)
    out = {
        "timestamp_ns": int(evt.ts_ns),
        "timestamp_iso": datetime.fromtimestamp(timestamp_seconds).isoformat() + "Z",
        "pid": int(evt.pid),
        "tgid": int(evt.tgid),
        "uid": int(evt.uid),
        "comm": _bytes_to_str(evt.comm),
        "saddr": int(evt.saddr),
        "daddr": int(evt.daddr),
        "sport": int(evt.sport),
        "dport": int(evt.dport),
        "ip_version": int(evt.ip_version),
    }
    print(json.dumps(out, ensure_ascii=False), flush=True)
    # Debug to stderr
    # sys.stderr.write(f"DEBUG: Captured network event pid={evt.pid}\n")

b["net_events"].open_perf_buffer(handle_event)

def exit_gracefully(signum, frame):
    print("\nDetaching and exiting.")
    sys.exit(0)

signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)

while True:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit_gracefully(None, None)
