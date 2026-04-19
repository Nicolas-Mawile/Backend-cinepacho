"""Application settings using pydantic-settings."""

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Cinepacho Backend"
    database_url: str = "sqlite+aiosqlite:///./cinepacho.db"

    class Config:
        env_file = ".env"


settings = Settings()
