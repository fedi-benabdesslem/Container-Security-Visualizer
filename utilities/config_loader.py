import yaml
import os
class Config:
    _instance = None
    _config = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    def _load_config(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "config",
            "config.yaml"
        )
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
    def get(self, key_path, default=None):
        env_key = key_path.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            if env_value.lower() == 'true': return True
            if env_value.lower() == 'false': return False
            try:
                if '.' in env_value: return float(env_value)
                return int(env_value)
            except ValueError:
                return env_value
        keys = key_path.split('.')
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    @property
    def ebpf_syscall_monitor(self):
        return self.get('ebpf.syscall_monitor')
    @property
    def ebpf_net_monitor(self):
        return self.get('ebpf.net_monitor')
    @property
    def collector_output_mode(self):
        return self.get('collector.output_mode', 'stdout')
    @property
    def collector_log_file(self):
        return self.get('collector.log_file')
    @property
    def collector_api_endpoint(self):
        return self.get('collector.api_endpoint', 'http://localhost:8000/api/events')
    @property
    def cache_ttl(self):
        return self.get('cache.pid_ttl_seconds', 60)
config = Config()
