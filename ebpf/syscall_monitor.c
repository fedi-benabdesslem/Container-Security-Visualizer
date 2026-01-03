#include <linux/ptrace.h>
#include <linux/sched.h>
#include <linux/tracepoint.h>
#include <linux/types.h>
#include <uapi/linux/ptrace.h>
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
struct execve_args {
  unsigned long long unused;
  int __syscall_nr;
  const char *filename;
  const char *const *argv;
  const char *const *envp;
};
int trace_execve(struct execve_args *args) {
  struct event_t evt = {};
  u64 pidtgid = bpf_get_current_pid_tgid();
  evt.tgid = pidtgid & 0xffffffff;
  evt.pid = pidtgid >> 32;
  evt.ts_ns = bpf_ktime_get_ns();
  evt.uid = bpf_get_current_uid_gid() & 0xffffffff;
  bpf_get_current_comm(&evt.comm, sizeof(evt.comm));
  if (args->filename) {
    bpf_probe_read_user_str(&evt.argv, sizeof(evt.argv),
                            (void *)args->filename);
  }
  events.perf_submit(args, &evt, sizeof(evt));
  return 0;
}