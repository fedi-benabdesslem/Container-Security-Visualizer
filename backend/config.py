#!/usr/bin/env python3
# config.py - Configuration management

import yaml
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_ROOT / "config" / "backend_config.yaml"


class ServerConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    reload: bool = True


class DatabaseConfig(BaseSettings):
    type: str = "postgresql"
    host: str = "localhost"
    port: int = 5432
    name: str = "container_security"
    user: str = "postgres"
    password: str = ""

    @property
    def url(self) -> str:
        """Generate database URL from config"""
        if self.type == "postgresql":
            # Use psycopg (psycopg3) driver instead of psycopg2
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
    allow_origins: List[str] = ["http://localhost:3000"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]


class LoggingConfig(BaseSettings):
    level: str = "INFO"
    file: str = "logs/backend.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class Config:
    """Main configuration class"""

    def __init__(self, config_file: Path = CONFIG_FILE):
        self.config_file = config_file
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file"""
        if not self.config_file.exists():
            print(f"Warning: Config file {self.config_file} not found. Using defaults.")
            config_data = {}
        else:
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}

        # Initialize all config sections
        self.server = ServerConfig(**config_data.get('server', {}))
        self.database = DatabaseConfig(**config_data.get('database', {}))
        self.websocket = WebSocketConfig(**config_data.get('websocket', {}))
        self.alerts = AlertsConfig(**config_data.get('alerts', {}))
        self.ingestion = IngestionConfig(**config_data.get('ingestion', {}))
        self.cors = CORSConfig(**config_data.get('cors', {}))
        self.logging = LoggingConfig(**config_data.get('logging', {}))


# Create global config instance
config = Config()
