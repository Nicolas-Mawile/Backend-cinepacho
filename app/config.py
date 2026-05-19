"""Application settings using pydantic-settings."""

from pydantic_settings import BaseSettings

from typing import Optional


class Settings(BaseSettings):
    """
    Configuración de la aplicación
    desde variables de entorno.
    """

    # ==========================================
    # APP
    # ==========================================

    app_name: str = "Cinepacho Backend"

    debug: bool = False

    # ==========================================
    # DATABASE
    # ==========================================

    database_url: str = (
        "postgresql://cinepacho_user:"
        "123456@localhost:5432/cinepacho"
    )

    # ==========================================
    # JWT
    # ==========================================

    secret_key: str = (
        "tu-clave-secreta-cambiar-en-produccion"
    )

    algorithm: str = "HS256"

    access_token_expire_minutes: int = 30

    # ==========================================
    # CORS
    # ==========================================

    cors_origins: str = (
        '["http://localhost:3000", '
        '"http://localhost:5173"]'
    )

    # ==========================================
    # EMAIL SMTP
    # ==========================================

    smtp_server: Optional[str] = None

    smtp_port: Optional[int] = None

    smtp_user: Optional[str] = None

    smtp_password: Optional[str] = None

    # ==========================================
    # BACKEND URL
    # ==========================================

    backend_url: str = (
        "http://localhost:8000"
    )

    # ==========================================
    # CONFIG
    # ==========================================

    class Config:

        env_file = ".env"

        case_sensitive = False

        extra = "ignore"


settings = Settings()