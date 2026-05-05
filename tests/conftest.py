"""Pytest fixtures for Cinepacho tests."""

import pytest
import app.infrastructure.models
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.infrastructure.models.base import Base
from app.database import get_db
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
