#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>
#include <linux/sched.h>
#include <linux/in.h>
#define COMM_LEN TASK_COMM_LEN
struct net_event_t {
    u64 ts_ns;
    u32 pid;
    u32 tgid;
    u32 uid;
    char comm[COMM_LEN];
    u32 saddr;
    u32 daddr;
    u16 sport;
    u16 dport;
    u8 ip_version;
};  BPF_PERF_OUTPUT(net_events);
int trace_connect(struct pt_regs *ctx, struct sock *sk) {
    if (!sk)
        return 0;
    u16 family = sk->__sk_common.skc_family;
    if (family != AF_INET)
        return 0;
    struct net_event_t evt = {};
    evt.ts_ns = bpf_ktime_get_ns();
    u64 pidtgid = bpf_get_current_pid_tgid();
    evt.tgid = pidtgid & 0xffffffff;
    evt.pid  = pidtgid >> 32;
    evt.uid = bpf_get_current_uid_gid() & 0xffffffff;
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));
    evt.saddr = sk->__sk_common.skc_rcv_saddr;
    evt.daddr = sk->__sk_common.skc_daddr;
    evt.sport = ntohs(sk->__sk_common.skc_num);
    evt.dport = ntohs(sk->__sk_common.skc_dport);
    evt.ip_version = 4;
    net_events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}