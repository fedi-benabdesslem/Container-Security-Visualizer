cmake_minimum_required(VERSION 4.0)
project(Container_Security_Visualizer C)

set(CMAKE_C_STANDARD 11)

add_executable(Container_Security_Visualizer
        ebpf/syscall_monitor.c
        ebpf/net_monitor.c)
include_directories(
    /usr/include
    /usr/include/bcc

    # Kernel includes
    /usr/src/kernels/6.17.8-300.fc43.x86_64/include
    /usr/src/kernels/6.17.8-300.fc43.x86_64/include/uapi
    /usr/src/kernels/6.17.8-300.fc43.x86_64/include/generated/uapi
)