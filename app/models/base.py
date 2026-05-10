"""Declarative base y mixins para modelos."""

from datetime import datetime, timezone
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy import Column, DateTime


@as_declarative()
class Base:
    id: int

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
