"""Schemas para peliculas."""

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