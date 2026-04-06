"""Centralized logging configuration for HealthBot."""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from healthbot.core.settings import settings

DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(level: int | None = None) -> None:
    """Configure root logging once for file and stdout handlers."""
    root_logger = logging.getLogger()
    if getattr(configure_logging, "_configured", False):
        return

    resolved_level = level or getattr(logging, settings.log_level.upper(), logging.INFO)
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(resolved_level)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(resolved_level)
    stream_handler.setFormatter(formatter)

    root_logger.setLevel(resolved_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    configure_logging._configured = True


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger configured via ``configure_logging``."""
    return logging.getLogger(name)
