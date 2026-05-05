"""Pytest fixtures for Cinepacho tests."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.main import app
from app.models.base import Base
from app.models.cliente import Cliente
from app.models.multiplex import Multiplex
from app.models.empleado import Empleado
from app.models.refrescar_token import RefreshToken
from app.models.cliente import Cliente
from app.models.multiplex import Multiplex
from app.models.empleado import Empleado
from app.models.refrescar_token import RefreshToken
from app.database import get_db
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_engine("sqlite:///:memory:", echo=False)
TestingSessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def cliente_normal(db_session):
    cliente = Cliente(
        nombre="Test User",
        correo="test@example.com",
        password_hash=pwd_context.hash("password123"),
        intentos_fallidos=0,
    )
    db_session.add(cliente)
    db_session.commit()
    db_session.refresh(cliente)
    return cliente

@pytest.fixture
def cliente_bloqueado(db_session):
    cliente = Cliente(
        nombre="Bloqueado User",
        correo="bloqueado@example.com",
        password_hash=pwd_context.hash("password123"),
        intentos_fallidos=5,
        ultimo_intento=datetime.now(timezone.utc),
    )
    db_session.add(cliente)
    db_session.commit()
    db_session.refresh(cliente)
    return cliente

@pytest_asyncio.fixture
async def http_client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()