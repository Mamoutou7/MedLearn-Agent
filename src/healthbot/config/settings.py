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

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY missing")

        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY missing")


settings = Settings()
print(settings.openai_api_key)
print(settings.tavily_api_key)
