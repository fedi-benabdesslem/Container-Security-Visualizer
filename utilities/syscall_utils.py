from typing import Optional, List
SECURITY_RELEVANT_SYSCALLS = {
    'execve', 'execveat', 'fork', 'vfork', 'clone', 'clone3',
    'setuid', 'setgid', 'setreuid', 'setregid', 'setresuid', 'setresgid',
    'capset', 'prctl',
    'open', 'openat', 'openat2', 'creat',
    'socket', 'connect', 'bind', 'listen', 'accept', 'accept4',
    'init_module', 'finit_module', 'delete_module',
    'mount', 'umount', 'umount2', 'pivot_root', 'chroot',
    'reboot', 'sethostname', 'setdomainname',
    'ptrace', 'process_vm_readv', 'process_vm_writev'
}
SYSCALL_CATEGORIES = {
    'process': ['execve', 'execveat', 'fork', 'vfork', 'clone', 'clone3', 'exit', 'exit_group'],
    'file': ['open', 'openat', 'openat2', 'creat', 'read', 'write', 'close', 'stat', 'fstat', 'lstat'],
    'network': ['socket', 'connect', 'bind', 'listen', 'accept', 'accept4', 'send', 'recv', 'sendto', 'recvfrom'],
    'privilege': ['setuid', 'setgid', 'setreuid', 'setregid', 'setresuid', 'setresgid', 'capset', 'prctl'],
    'ipc': ['pipe', 'pipe2', 'msgget', 'msgsnd', 'msgrcv', 'shmget', 'shmat', 'shmdt', 'semget', 'semop'],
    'system': ['mount', 'umount', 'umount2', 'reboot', 'sethostname', 'setdomainname', 'init_module', 'finit_module']
}
def parse_syscall_name(argv: str) -> Optional[str]:
    if not argv:
        return None
    return 'execve'
def is_security_relevant_syscall(syscall_name: str) -> bool:
    return syscall_name.lower() in SECURITY_RELEVANT_SYSCALLS
def categorize_syscall(syscall_name: str) -> List[str]:
    categories = []
    syscall_lower = syscall_name.lower()
    for category, syscalls in SYSCALL_CATEGORIES.items():
        if syscall_lower in syscalls:
            categories.append(category)
    return categories if categories else ['unknown']
def get_risk_score(syscall_name: str, uid: int = None) -> int:
    score = 0
    syscall_lower = syscall_name.lower()
    if is_security_relevant_syscall(syscall_lower):
        score += 3
    if syscall_lower in ['setuid', 'setgid', 'capset', 'prctl']:
        score += 4
    if syscall_lower in ['init_module', 'finit_module', 'delete_module']:
        score += 5
    if syscall_lower in ['mount', 'umount', 'pivot_root', 'chroot']:
        score += 4
    if uid is not None and uid != 0 and score > 0:
        score += 2
    return min(score, 10)