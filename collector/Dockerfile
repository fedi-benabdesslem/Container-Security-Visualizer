FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies for BCC
RUN apt-get update && apt-get install -y \
    bpfcc-tools \
    python3-bpfcc \
    python3-pip \
    python3-docker \
    python3-yaml \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# The collector needs access to kernel headers
# These are typically mounted from the host at /usr/src or /lib/modules

COPY collector ./collector
COPY ebpf ./ebpf
COPY utilities ./utilities
COPY config ./config

# No requirements.txt needed if we install everything via apt (more stable for BCC)
# But let's check if there are extra dependencies
COPY backend/requirements.txt ./requirements_backend.txt
# Only install what's missing and needed by collector/utilities
RUN pip3 install requests python-dotenv

# Run collector
# Note: This will need to be run with --privileged and host mounts
CMD ["python3", "collector/collector.py"]
