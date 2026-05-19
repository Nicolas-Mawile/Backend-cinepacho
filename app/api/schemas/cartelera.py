"""Schemas para cartelera."""

from pydantic import BaseModel


class CarteleraAdd(BaseModel):
    peliculaId: int