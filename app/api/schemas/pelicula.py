"""Schemas de películas."""

from typing import Optional
from pydantic import BaseModel


class PeliculaCreate(BaseModel):
    titulo: str
    duracionMinutos: int
    linkTrailer: Optional[str] = None
    linkPoster: Optional[str] = None
    sinopsis: Optional[str] = None


class PeliculaUpdate(BaseModel):
    titulo: Optional[str] = None
    duracionMinutos: Optional[int] = None
    linkTrailer: Optional[str] = None
    linkPoster: Optional[str] = None
    sinopsis: Optional[str] = None


class PeliculaResponse(BaseModel):
    id: int
    titulo: str
    duracionMinutos: int
    linkTrailer: Optional[str] = None
    linkPoster: Optional[str] = None
    sinopsis: Optional[str] = None
    estaActiva: bool

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class CambiarEstadoPeliculaRequest(BaseModel):
    estaActiva: bool


class CambiarEstadoPeliculaResponse(BaseModel):
    mensaje: str
    pelicula: PeliculaResponse
