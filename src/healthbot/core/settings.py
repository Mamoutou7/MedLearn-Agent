"""
Application configuration module.

Handles environment variable loading and validation.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """
    Immutable application settings.

    Attributes
    ----------
    openai_api_key : str
        API key used for OpenAI services.

    tavily_api_key : str
        API key used for Tavily search.
    """

    openai_api_key: str
    tavily_api_key: str
    model_name: str

    @classmethod
    def load(cls) -> "Settings":
        """
        Load settings from environment variables.

        Returns
        -------
        Settings
        """
        load_dotenv()

        openai = os.getenv("OPENAI_API_KEY")
        tavily = os.getenv("TAVILY_API_KEY")
        model = os.getenv("MODEL_NAME")

        if not openai:
            raise EnvironmentError("OPENAI_API_KEY missing")

        if not tavily:
            raise EnvironmentError("TAVILY_API_KEY missing")
        if not model:
            raise EnvironmentError("MODEL_NAME missing")

        return cls(openai_api_key=openai, tavily_api_key=tavily, model_name=model)


settings = Settings.load()
