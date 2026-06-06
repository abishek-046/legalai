"""
Application configuration using pydantic-settings
Supabase version - replaces MongoDB settings with Supabase credentials.
"""

import json
from pydantic_settings import BaseSettings
from typing import List, Union


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # JWT
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # OpenAI
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""  # Free at https://console.groq.com
    OCR_SPACE_API_KEY: str = "helloworld"  # Free OCR.space demo key

    # App
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://legalai-q2y8.vercel.app",
    ]

    # Legacy - ignored but kept to avoid validation errors if still in env
    MONGODB_URL: str = ""
    DATABASE_NAME: str = ""

    @property
    def origins_list(self) -> List[str]:
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        raw = self.ALLOWED_ORIGINS.strip()
        if raw.startswith("["):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass
        return [o.strip() for o in raw.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
