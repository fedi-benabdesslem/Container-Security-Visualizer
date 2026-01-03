import logging
import sys
from pathlib import Path
from backend.config import config
def setup_logger(name: str = "backend") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.logging.level))
    if logger.handlers:
        return logger
    formatter = logging.Formatter(config.logging.format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    from logging.handlers import RotatingFileHandler
    log_file = Path(config.logging.file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
logger = setup_logger()
