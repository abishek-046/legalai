"""
Application configuration using pydantic-settings
Supports both local .env files and cloud environment variables.
ALLOWED_ORIGINS can be a JSON array or a comma-separated string.
"""

import json
from pydantic_settings import BaseSettings
from typing import List, Union


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "legal_assistant"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    OPENAI_API_KEY: str = ""
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://legalai-q2y8.vercel.app",
    ]

    @property
    def origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS whether it's a list, JSON string, or comma-separated string."""
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        raw = self.ALLOWED_ORIGINS.strip()
        # Try JSON array first
        if raw.startswith("["):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass
        # Fall back to comma-separated
        return [o.strip() for o in raw.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
