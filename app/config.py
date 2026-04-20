"""Application settings using pydantic-settings."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Cinepacho Backend"
    database_url: str = "sqlite+aiosqlite:///./cinepacho.db"
    secret_key: str = "supersecretkey_cambiar_despues_idk"
    algorithm: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()