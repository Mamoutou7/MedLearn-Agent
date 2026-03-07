"""
Custom exceptions used across the HealthBot application.

This module centralizes domain-specific exceptions in order to:
- improve error readability
- simplify debugging
- avoid using generic Exception types
"""

from typing import Optional


class HealthBotError(Exception):
    """
    Base exception class for all HealthBot related errors.
    """

    def __init__(self, message: str, context: Optional[dict] = None):
        """
        Parameters
        ----------
        message : str
            Human readable error description
        context : Optional[dict]
            Additional contextual debugging data
        """
        super().__init__(message)
        self.context = context or {}


class ConfigurationError(HealthBotError):
    """
    Raised when application configuration is invalid or incomplete.
    """
    pass

class ValidationError(HealthBotError):
    """
    Raised when a user request fails domain validation.
    """
    pass

class LLMServiceError(HealthBotError):
    """
    Raised when interaction with the LLM fails.
    """
    pass

class ToolExecutionError(HealthBotError):
    """
    Raised when an external tool fails (web search, API calls, etc.).
    """
    pass

class WorkflowError(HealthBotError):
    """
    Raised when the LangGraph workflow encounters an invalid state.
    """
    pass

class QuizGenerationError(HealthBotError):
    pass

class QuizGradingError(HealthBotError):
    pass