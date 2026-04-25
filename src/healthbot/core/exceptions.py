"""
Custom exceptions used across the HealthBot application.
"""

from __future__ import annotations


class HealthBotError(Exception):
    """Base exception class for all HealthBot related errors."""

    status_code = 400

    def __init__(self, message: str, context: dict | None = None):
        super().__init__(message)
        self.context = context or {}


class ConfigurationError(HealthBotError):
    """Raised when application configuration is invalid or incomplete."""

    status_code = 500


class ValidationError(HealthBotError):
    """Raised when a user request fails domain validation."""

    status_code = 422


class LLMServiceError(HealthBotError):
    """Raised when interaction with the LLM fails."""

    status_code = 502


class ToolExecutionError(HealthBotError):
    """Raised when an external tool fails."""

    status_code = 502


class WorkflowError(HealthBotError):
    """Raised when the LangGraph e2e encounters an invalid state."""

    status_code = 400


class SessionBackendUnavailableError(HealthBotError):
    """Raised when the configured session backend is unavailable."""

    status_code = 503


class QuizGenerationError(HealthBotError):
    status_code = 500


class QuizGradingError(HealthBotError):
    status_code = 500


class CheckpointerFactoryError(RuntimeError):
    pass
