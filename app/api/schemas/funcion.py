"""Schemas para funciones."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.api.schemas.multiplex import MultiplexSummaryResponse
from app.api.schemas.pelicula import PeliculaResponse


class FuncionCreate(BaseModel):
    peliculaId: int
    salaId: int
    fechaHora: datetime


class FuncionUpdate(BaseModel):
    peliculaId: int | None = None
    salaId: int | None = None
    fechaHora: datetime | None = None


class SalaFuncionResponse(BaseModel):
    id: int
    numero: int
    activa: bool = Field(alias="estaActiva")
    multiplexId: int
    multiplex: MultiplexSummaryResponse

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class FuncionResponse(BaseModel):
    id: int
    peliculaId: int
    salaId: int
    fechaHora: datetime
    fechaHoraFin: datetime
    activa: bool = Field(alias="estaActiva")
    pelicula: PeliculaResponse
    sala: SalaFuncionResponse

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class SillaDisponibilidadResponse(BaseModel):
    sillaId: int
    fila: int
    columna: int
    tipo: str | None = None
    estado: str

    model_config = {
        "from_attributes": True,
    }


class FuncionDetalleResponse(BaseModel):
    id: int
    peliculaId: int
    salaId: int
    fechaHora: datetime
    fechaHoraFin: datetime
    activa: bool = Field(alias="estaActiva")

    pelicula: PeliculaResponse
    sala: SalaFuncionResponse

    sillas: list[SillaDisponibilidadResponse]

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }