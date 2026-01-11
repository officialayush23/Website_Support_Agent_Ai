# app/core/config.py

from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str

    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str

    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
