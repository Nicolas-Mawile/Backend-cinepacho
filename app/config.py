"""Application settings using pydantic-settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación desde variables de entorno."""
    
    # App
    app_name: str = "Cinepacho Backend"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./cinepacho.db"
    
    # JWT
    secret_key: str = "tu-clave-secreta-cambiar-en-produccion"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
