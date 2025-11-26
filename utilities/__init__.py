#!/usr/bin/env python3
# __init__.py
# Makes 'common' a Python package and provides convenient imports

from .docker_utils import (
    get_container_id_from_pid,
    get_container_metadata,
    is_containerized
)

from .syscall_utils import (
    parse_syscall_name,
    is_security_relevant_syscall,
    categorize_syscall
)

__all__ = [
    'get_container_id_from_pid',
    'get_container_metadata',
    'is_containerized',
    'parse_syscall_name',
    'is_security_relevant_syscall',
    'categorize_syscall'
]
