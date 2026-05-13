"""Pytest fixtures for Cinepacho tests."""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.models.base import Base
from app.infrastructure.models.cliente import Cliente
from app.database import get_db
from app.domain.services.auth_service import AuthService
import app.infrastructure.models  # Asegurar que todos los modelos se registren en Base


@pytest.fixture
def db_session():
    """BD síncrona en memoria para tests."""
    # Usar una base de datos SQLite en disco temporal para evitar problemas de conexión compartida
    import os
    db_file = "test_db.sqlite"
    if os.path.exists(db_file):
        os.remove(db_file)
        
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    
    with SessionLocal() as session:
        # Sobrescribir la dependencia get_db de FastAPI para que use esta sesión
        def override_get_db():
            yield session
        
        from app.main import app
        app.dependency_overrides[get_db] = override_get_db
        
        yield session
        
        app.dependency_overrides.clear()

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists(db_file):
        os.remove(db_file)


@pytest.fixture
def cliente_normal(db_session):
    """Fixture para un cliente normal sin bloqueo."""
    auth_service = AuthService()
    cliente = Cliente(
        nombre_completo="Test User",
        correo="test@example.com",
        password_hash=auth_service.hashPassword("password123"),
        intentos_fallidos=0,
    )
    db_session.add(cliente)
    db_session.commit()
    db_session.refresh(cliente)
    return cliente


@pytest.fixture
def cliente_bloqueado(db_session):
    """Fixture para un cliente bloqueado."""
    auth_service = AuthService()
    cliente = Cliente(
        nombre_completo="Bloqueado User",
        correo="bloqueado@example.com",
        password_hash=auth_service.hashPassword("password123"),
        intentos_fallidos=5,
        bloqueado_hasta=datetime.now(timezone.utc),
    )
    db_session.add(cliente)
    db_session.commit()
    db_session.refresh(cliente)
    return cliente
