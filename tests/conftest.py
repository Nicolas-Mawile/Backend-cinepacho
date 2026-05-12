"""Pytest fixtures for Cinepacho tests."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker
from app.main import app
from app.infrastructure.models.multiplex_cartelera import MultiplexCartelera
from app.infrastructure.models.pelicula import Pelicula
from app.infrastructure.models.base import Base as InfraBase
from app.infrastructure import models as _infra_models
from app.models.base import Base as LegacyBase
from app.models.cliente import Cliente as AuthCliente
from app.models.multiplex import Multiplex as _legacy_multiplex
from app.models.empleado import Empleado as _legacy_empleado
from app.models.refrescar_token import RefreshToken
from app.database import get_db
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_engine(
    "sqlite://",
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

@pytest.fixture(autouse=True)
def setup_db():
    LegacyBase.metadata.create_all(bind=engine)
    InfraBase.metadata.create_all(bind=engine)
    yield
    InfraBase.metadata.drop_all(bind=engine)
    LegacyBase.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def cliente_normal(db_session):
    cliente = AuthCliente(
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
    cliente = AuthCliente(
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