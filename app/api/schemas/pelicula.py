"""Schemas de películas."""

from pydantic import BaseModel

from typing import Optional


# =========================================================
# REQUESTS
# =========================================================

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


# =========================================================
# RESPONSES
# =========================================================

class PeliculaResponse(BaseModel):

    id: int

    titulo: str

    duracionMinutos: int

    linkTrailer: Optional[str]

    linkPoster: Optional[str]

    sinopsis: Optional[str]

    estaActiva: bool

    class Config:

        from_attributes = True

class CambiarEstadoPeliculaRequest(BaseModel):

    estaActiva: bool

class CambiarEstadoPeliculaResponse(BaseModel):

    mensaje: str

    pelicula: PeliculaResponse
"""Schemas para peliculas."""

from typing import Optional

from pydantic import BaseModel, Field


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
    activa: bool = Field(alias="estaActiva")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }