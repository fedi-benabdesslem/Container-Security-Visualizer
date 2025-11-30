syscall_monitor.py
# BCC-based loader for syscall_monitor.c — reads perf buffer and prints JSON-like events.

net_monitor.py
# BCC-based loader for net_monitor.c — monitors TCP connection events
# Captures source/dest IPs, ports, and process metadata

# Run as root.both scripts 

net_monitor.c
# BCC-based eBPF program to monitor TCP connection attempts

syscall_monitor.c
# BCC-based eBPF program to monitor execve syscalls
# Built to be loaded with BCC (Python).