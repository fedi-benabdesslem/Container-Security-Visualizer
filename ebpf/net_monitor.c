// net_monitor.c
// BCC-based eBPF program to monitor TCP connection attempts
// Captures source/destination IPs, ports, and process metadata

#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>
#include <linux/sched.h>

#define COMM_LEN TASK_COMM_LEN

struct net_event_t {
    u64 ts_ns;
    u32 pid;
    u32 tgid;
    u32 uid;
    char comm[COMM_LEN];
    u32 saddr;      // source IP (IPv4)
    u32 daddr;      // destination IP (IPv4)
    u16 sport;      // source port
    u16 dport;      // destination port
    u8 ip_version;  // 4 for IPv4, 6 for IPv6
};

BPF_PERF_OUTPUT(net_events);

// Hook into TCP connect - captures outgoing connection attempts
// This kprobe fires when a process initiates a TCP connection
int trace_connect(struct pt_regs *ctx, struct sock *sk)
{
    // Filter: only capture IPv4 TCP connections
    u16 family = sk->__sk_common.skc_family;
    if (family != AF_INET) {
        return 0;  // Skip IPv6 and other protocols for now
    }

    struct net_event_t evt = {};

    // Get timestamp
    evt.ts_ns = bpf_ktime_get_ns();

    // Get PID/TGID
    u64 pidtgid = bpf_get_current_pid_tgid();
    evt.tgid = pidtgid & 0xffffffff;
    evt.pid  = pidtgid >> 32;

    // Get UID
    evt.uid = bpf_get_current_uid_gid() & 0xffffffff;

    // Get process name
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));

    // Extract network info from socket structure
    evt.saddr = sk->__sk_common.skc_rcv_saddr;  // source IP
    evt.daddr = sk->__sk_common.skc_daddr;      // destination IP
    evt.sport = sk->__sk_common.skc_num;        // source port
    evt.dport = sk->__sk_common.skc_dport;      // destination port (network byte order)

    // Convert destination port from network byte order to host byte order
    evt.dport = ntohs(evt.dport);

    evt.ip_version = 4;

    // Submit event to user space
    net_events.perf_submit(ctx, &evt, sizeof(evt));

    return 0;
}

// Alternative: Hook TCP state changes to catch connections
// This gives us more connection lifecycle visibility
/*
TRACEPOINT_PROBE(sock, inet_sock_set_state)
{
    // Only capture TCP_ESTABLISHED state (successful connections)
    if (args->protocol != IPPROTO_TCP)
        return 0;

    // Filter for new connections (state change to ESTABLISHED)
    if (args->newstate != 1)  // TCP_ESTABLISHED = 1
        return 0;

    // Only IPv4 for now
    if (args->family != AF_INET)
        return 0;

    struct net_event_t evt = {};

    evt.ts_ns = bpf_ktime_get_ns();

    u64 pidtgid = bpf_get_current_pid_tgid();
    evt.tgid = pidtgid & 0xffffffff;
    evt.pid  = pidtgid >> 32;

    evt.uid = bpf_get_current_uid_gid() & 0xffffffff;

    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));

    // Extract IPs from byte arrays - IPv4 addresses are 4 bytes
    // Copy the 4-byte array into our u32 fields
    __builtin_memcpy(&evt.saddr, args->saddr, 4);
    __builtin_memcpy(&evt.daddr, args->daddr, 4);

    evt.sport = args->sport;
    evt.dport = args->dport;

    evt.ip_version = 4;

    net_events.perf_submit(args, &evt, sizeof(evt));

    return 0;
}
*/