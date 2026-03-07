"""
Centralized logging configuration for HealthBot.

Provides structured logging and reusable logger instances
across the application.

Logs are written only to a rotating file.
"""

import logging
from typing import Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler


DEFAULT_LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure global logging behavior.

    Logs are written only to logs/healthbot.log
    """

    root_logger = logging.getLogger()

    # Prevent reconfiguration
    if root_logger.handlers:
        return

    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "healthbot.log"

    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5_000_000,  # 5 MB
        backupCount=3
    )

    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a configured logger instance.
    """

    logger = logging.getLogger(name)
    logger.propagate = True

    return logger