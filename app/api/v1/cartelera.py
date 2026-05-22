"""Legacy compatibility re-exports for cartelera."""

from app.api.cartelera import (
    agregar_a_cartelera,
    agregar_a_cartelera_general,
    remover_de_cartelera,
    remover_de_cartelera_general,
    ver_cartelera,
    ver_cartelera_general,
)
from app.api.schemas.cartelera import CarteleraAdd as CartelераAdd

__all__ = [
    "CarteleraAdd",
    "CartelераAdd",
    "ver_cartelera_general",
    "ver_cartelera",
    "agregar_a_cartelera",
    "remover_de_cartelera",
    "agregar_a_cartelera_general",
    "remover_de_cartelera_general",
]
