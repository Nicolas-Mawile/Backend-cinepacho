"""Schemas para funciones."""

from datetime import datetime
from pydantic import BaseModel


class FuncionCreate(BaseModel):
    peliculaId: int
    salaId: int
    fechaHora: datetime


class FuncionUpdate(BaseModel):
    peliculaId: int | None = None
    salaId: int | None = None
    fechaHora: datetime | None = None