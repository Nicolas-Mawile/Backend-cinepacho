"""Schemas para cartelera."""

from pydantic import BaseModel

from app.api.schemas.multiplex import MultiplexSummaryResponse
from app.api.schemas.pelicula import PeliculaResponse


class CarteleraAdd(BaseModel):
    peliculaId: int


class CarteleraItemResponse(BaseModel):
    id: int
    multiplexId: int
    peliculaId: int
    multiplex: MultiplexSummaryResponse
    pelicula: PeliculaResponse

    model_config = {
        "from_attributes": True,
    }


class CarteleraGeneralResponse(BaseModel):
    peliculas: list[PeliculaResponse]