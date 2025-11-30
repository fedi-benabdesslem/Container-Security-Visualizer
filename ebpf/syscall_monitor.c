#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/types.h>
#include <linux/tracepoint.h>
#include <linux/ptrace.h>
#define ARGV_LEN 128
#define COMM_LEN TASK_COMM_LEN
struct event_t {
    u64 ts_ns;
    u32 pid;
    u32 tgid;
    u32 uid;
    char comm[COMM_LEN];
    char argv[ARGV_LEN];
};
BPF_PERF_OUTPUT(events);
TRACEPOINT_PROBE(syscalls, sys_enter_execve) {
    struct event_t evt = {};
    u64 pidtgid = bpf_get_current_pid_tgid();
    evt.tgid = pidtgid & 0xffffffff;
    evt.pid  = pidtgid >> 32;
    evt.ts_ns = bpf_ktime_get_ns();
    evt.uid = bpf_get_current_uid_gid() & 0xffffffff;
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));
    bpf_probe_read_user_str(&evt.argv, sizeof(evt.argv), (void *)args->filename);
    events.perf_submit(args, &evt, sizeof(evt));
    return 0;
}