import os
import sys
from utilities import config
print("Testing config loader...")
print(f"✅ Syscall monitor: {config.ebpf_syscall_monitor}")
print(f"✅ Network monitor: {config.ebpf_net_monitor}")
print(f"✅ Output mode: {config.collector_output_mode}")
print(f"✅ API endpoint: {config.collector_api_endpoint}")
print(f"✅ Cache TTL: {config.cache_ttl} seconds")
print("\n✅ Config loaded successfully!")
