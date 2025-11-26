#!/usr/bin/env python3
# syscall_utils.py
# Utilities for analyzing and categorizing system calls

from typing import Optional, List

# Security-relevant syscalls that might indicate suspicious activity
SECURITY_RELEVANT_SYSCALLS = {
    # Process manipulation
    'execve', 'execveat', 'fork', 'vfork', 'clone', 'clone3',

    # Privilege escalation
    'setuid', 'setgid', 'setreuid', 'setregid', 'setresuid', 'setresgid',
    'capset', 'prctl',

    # File access
    'open', 'openat', 'openat2', 'creat',

    # Network
    'socket', 'connect', 'bind', 'listen', 'accept', 'accept4',

    # Module loading
    'init_module', 'finit_module', 'delete_module',

    # System configuration
    'mount', 'umount', 'umount2', 'pivot_root', 'chroot',
    'reboot', 'sethostname', 'setdomainname',

    # Monitoring evasion
    'ptrace', 'process_vm_readv', 'process_vm_writev'
}

# Categorization of syscalls by type
SYSCALL_CATEGORIES = {
    'process': ['execve', 'execveat', 'fork', 'vfork', 'clone', 'clone3', 'exit', 'exit_group'],
    'file': ['open', 'openat', 'openat2', 'creat', 'read', 'write', 'close', 'stat', 'fstat', 'lstat'],
    'network': ['socket', 'connect', 'bind', 'listen', 'accept', 'accept4', 'send', 'recv', 'sendto', 'recvfrom'],
    'privilege': ['setuid', 'setgid', 'setreuid', 'setregid', 'setresuid', 'setresgid', 'capset', 'prctl'],
    'ipc': ['pipe', 'pipe2', 'msgget', 'msgsnd', 'msgrcv', 'shmget', 'shmat', 'shmdt', 'semget', 'semop'],
    'system': ['mount', 'umount', 'umount2', 'reboot', 'sethostname', 'setdomainname', 'init_module', 'finit_module']
}


def parse_syscall_name(argv: str) -> Optional[str]:
    """
    Extract syscall name from argv or command path.

    Examples:
        '/usr/bin/ls' -> 'execve'
        'open' -> 'open'

    Returns syscall name or None if can't be determined.
    """
    if not argv:
        return None

    # For now, we primarily track execve from our monitors
    # This can be extended based on what data your monitors capture
    return 'execve'


def is_security_relevant_syscall(syscall_name: str) -> bool:
    """
    Check if a syscall is considered security-relevant.

    Args:
        syscall_name: Name of the syscall (e.g., 'execve', 'setuid')

    Returns:
        True if syscall is security-relevant, False otherwise
    """
    return syscall_name.lower() in SECURITY_RELEVANT_SYSCALLS


def categorize_syscall(syscall_name: str) -> List[str]:
    """
    Categorize a syscall into one or more categories.

    Args:
        syscall_name: Name of the syscall

    Returns:
        List of category names, or ['unknown'] if not categorized
    """
    categories = []
    syscall_lower = syscall_name.lower()

    for category, syscalls in SYSCALL_CATEGORIES.items():
        if syscall_lower in syscalls:
            categories.append(category)

    return categories if categories else ['unknown']


def get_risk_score(syscall_name: str, uid: int = None) -> int:
    """
    Assign a risk score to a syscall (0-10 scale).
    Higher scores indicate more suspicious activity.

    Args:
        syscall_name: Name of the syscall
        uid: User ID executing the syscall (optional)

    Returns:
        Risk score (0-10)
    """
    score = 0
    syscall_lower = syscall_name.lower()

    # Base score for security-relevant syscalls
    if is_security_relevant_syscall(syscall_lower):
        score += 3

    # Higher risk for privilege-related syscalls
    if syscall_lower in ['setuid', 'setgid', 'capset', 'prctl']:
        score += 4

    # Higher risk for module loading
    if syscall_lower in ['init_module', 'finit_module', 'delete_module']:
        score += 5

    # Higher risk for system modification
    if syscall_lower in ['mount', 'umount', 'pivot_root', 'chroot']:
        score += 4

    # Bonus risk if executed by non-root (possible privilege escalation attempt)
    if uid is not None and uid != 0 and score > 0:
        score += 2

    return min(score, 10)  # Cap at 10
