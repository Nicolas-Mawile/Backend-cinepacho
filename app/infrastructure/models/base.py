"""Declarative base y mixins para modelos."""

from datetime import datetime, timezone
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy import Column, DateTime, Integer


@as_declarative()
class Base:
    id = Column(Integer, primary_key=True, index=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
