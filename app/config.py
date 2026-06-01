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
    # RESEND (email HTTP API)
    # ==========================================

    resend_api_key: Optional[str] = None

    email_from: str = "Cine Pacho <onboarding@resend.dev>"

    # ==========================================
    # BACKEND URL
    # ==========================================

    backend_url: str = (
        "http://localhost:8000"
    )

    # ==========================================
    # FRONTEND URL
    # En producción sobreescribir con FRONTEND_URL=https://tu-dominio.com
    # ==========================================

    frontend_url: str = (
        "http://localhost:5173"
    )

    # ==========================================
    # CONFIG
    # ==========================================

    class Config:

        env_file = ".env"

        case_sensitive = False

        extra = "ignore"


settings = Settings()