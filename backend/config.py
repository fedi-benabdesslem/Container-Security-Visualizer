import yaml
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_ROOT / "config" / "backend_config.yaml"
class ServerConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8002
    debug: bool = False
    reload: bool = False
    model_config = SettingsConfigDict(env_prefix="BACKEND_", env_file=".env", extra="ignore")
class DatabaseConfig(BaseSettings):
    type: str = "postgresql"
    host: str = "localhost"
    port: int = 5432
    name: str = "container_security"
    user: str = "postgres"
    password: str = "datasec1"
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")
    @property
    def url(self) -> str:
        if self.type == "postgresql":
            return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        elif self.type == "sqlite":
            return f"sqlite:///{self.name}.db"
        else:
            raise ValueError(f"Unsupported database type: {self.type}")
class WebSocketConfig(BaseSettings):
    max_connections: int = 100
    heartbeat_interval: int = 30
class AlertsConfig(BaseSettings):
    high_risk_threshold: int = 7
class IngestionConfig(BaseSettings):
    max_batch_size: int = 100
class CORSConfig(BaseSettings):
    allow_origins: List[str] = ["http://localhost:8080", "http://127.0.0.1:8080"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]
    @classmethod
    def from_env(cls, origins_str: str = None):
        if origins_str:
            origins = [o.strip() for o in origins_str.split(",")]
            return cls(allow_origins=origins)
        return cls()
class LoggingConfig(BaseSettings):
    level: str = "INFO"
    file: str = "logs/backend.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
class Config:
    def __init__(self, config_file: Path = CONFIG_FILE):
        self.config_file = config_file
        self._load_config()
    def _load_config(self):
        config_data = {}
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
        self.server = ServerConfig(**config_data.get('server', {}))
        self.database = DatabaseConfig(**config_data.get('database', {}))
        self.websocket = WebSocketConfig(**config_data.get('websocket', {}))
        self.alerts = AlertsConfig(**config_data.get('alerts', {}))
        self.ingestion = IngestionConfig(**config_data.get('ingestion', {}))
        cors_data = config_data.get('cors', {})
        env_origins = os.getenv("CORS_ORIGINS")
        if env_origins:
            self.cors = CORSConfig.from_env(env_origins)
        else:
            self.cors = CORSConfig(**cors_data)
        self.logging = LoggingConfig(**config_data.get('logging', {}))
config = Config()
