"""Pytest fixtures for Cinepacho tests."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.base import Base
from app.models.cliente import Cliente
from app.database import get_db
from passlib.context import CryptContext

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_async_engine(DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def cliente_normal(db_session):
    cliente = Cliente(
        nombre="Test User",
        correo="test@example.com",
        password_hash=pwd_context.hash("password123"),
        intentos_fallidos=0,
    )
    db_session.add(cliente)
    await db_session.commit()
    await db_session.refresh(cliente)
    return cliente

@pytest_asyncio.fixture
async def cliente_bloqueado(db_session):
    from datetime import datetime
    cliente = Cliente(
        nombre="Bloqueado User",
        correo="bloqueado@example.com",
        password_hash=pwd_context.hash("password123"),
        intentos_fallidos=5,
        ultimo_intento=datetime.now(timezone.utc),
    )
    db_session.add(cliente)
    await db_session.commit()
    await db_session.refresh(cliente)
    return cliente

@pytest_asyncio.fixture
async def http_client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()