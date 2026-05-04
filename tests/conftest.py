"""Pytest fixtures for Cinepacho tests."""

import pytest
import app.infrastructure.models
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.infrastructure.models.base import Base


@pytest.fixture
def db_session():
    """BD síncrona en memoria para tests."""
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )

    with SessionLocal() as session:
        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
