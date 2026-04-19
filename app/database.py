"""Database setup and dependency helpers."""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .config import settings


engine: AsyncEngine = create_async_engine(settings.database_url, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_db():
    raise NotImplementedError("Implement get_db dependency")


def get_local_db():
    raise NotImplementedError("Implement local DB access")
