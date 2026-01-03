from bcc import BPF
from datetime import datetime
import json
import os
import signal
import sys
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
C_FILE = os.path.join(THIS_DIR, "syscall_monitor.c")
b = BPF(src_file=C_FILE)
b.attach_tracepoint(tp="syscalls:sys_enter_execve", fn_name="trace_execve")
print("Loaded BPF program and attached to execve tracepoint. Listening for events... (CTRL-C to exit)")
def _bytes_to_str(b):
    if not b:
        return ""
    try:
        return b.decode('utf-8', 'ignore').rstrip("\x00")
    except Exception:
        return str(b)
def get_boot_time():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        return datetime.now().timestamp() - uptime_seconds
BOOT_TIME_OFFSET = get_boot_time()
def handle_event(cpu, data, size):
    evt = b["events"].event(data)
    timestamp_seconds = BOOT_TIME_OFFSET + (evt.ts_ns / 1e9)
    out = {
        "timestamp_ns": int(evt.ts_ns),
        "timestamp_iso": datetime.fromtimestamp(timestamp_seconds).isoformat() + "Z",
        "pid": int(evt.pid),
        "tgid": int(evt.tgid),
        "uid": int(evt.uid),
        "comm": _bytes_to_str(evt.comm),
        "argv": _bytes_to_str(evt.argv),
        "syscall_name": "execve"
    }
    print(json.dumps(out, ensure_ascii=False), flush=True)
b["events"].open_perf_buffer(handle_event)
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