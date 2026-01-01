#include <bcc/proto.h>
#include <linux/sched.h>
#include <uapi/linux/in.h>
#include <uapi/linux/in6.h>
#include <uapi/linux/ptrace.h>
#include <uapi/linux/unistd.h>

#define COMM_LEN TASK_COMM_LEN

struct net_event_t {
  u64 ts_ns;
  u32 pid;
  u32 tgid;
  u32 uid;
  char comm[COMM_LEN];
  u32 saddr; // will be 0 for outgoing connect (no local addr known here)
  u32 daddr;
  u16 sport; // 0 here (unless you extend code)
  u16 dport;
  u8 ip_version;
};

BPF_PERF_OUTPUT(net_events);

struct connect_args {
  unsigned long long unused;
  int __syscall_nr;
  int fd;
  struct sockaddr *uservaddr;
  int addrlen;
};

int trace_connect(struct connect_args *args) {
  struct sockaddr_in sa4 = {};
  u16 family = 0;

  if (args->uservaddr &&
      bpf_probe_read_user(&sa4, sizeof(sa4), (void *)args->uservaddr) < 0)
    return 0;

  family = sa4.sin_family;
  if (family != AF_INET)
    return 0;

  struct net_event_t evt = {};
  evt.ts_ns = bpf_ktime_get_ns();

  u64 pidtgid = bpf_get_current_pid_tgid();
  evt.tgid = pidtgid & 0xffffffff;
  evt.pid = pidtgid >> 32;
  evt.uid = bpf_get_current_uid_gid() & 0xffffffff;

  bpf_get_current_comm(&evt.comm, sizeof(evt.comm));

  evt.daddr = sa4.sin_addr.s_addr;
  evt.dport = ntohs(sa4.sin_port);
  evt.saddr = 0;
  evt.sport = 0;
  evt.ip_version = 4;

  net_events.perf_submit(args, &evt, sizeof(evt));
  return 0;
}
