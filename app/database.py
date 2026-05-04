"""Database setup and dependency helpers."""

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .config import settings
from .infrastructure.models.base import Base


# Crear engine síncrono
engine: Engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

# Factory de sesiones síncronas
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
)


def init_db():
    """Inicializa las tablas en la base de datos."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependencia para obtener sesión de BD en endpoints."""
    with SessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise

