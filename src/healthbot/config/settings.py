"""
Application configuration loader.
"""

import os
from dotenv import load_dotenv


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        load_dotenv()

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.model_name = os.getenv("MODEL_NAME")

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY missing")

        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY missing")


settings = Settings()