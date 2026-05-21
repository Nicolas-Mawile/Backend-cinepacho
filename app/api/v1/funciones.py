"""Legacy compatibility re-exports for funciones."""

from app.api.funciones import (
    crear_funcion,
    editar_funcion,
    eliminar_funcion,
    funciones_por_multiplex,
    funciones_por_pelicula,
    funciones_por_sala,
    funciones_pelicula_por_multiplex,
)
from app.api.schemas.funcion import FuncionCreate, FuncionUpdate

__all__ = [
    "FuncionCreate",
    "FuncionUpdate",
    "crear_funcion",
    "funciones_por_multiplex",
    "funciones_por_sala",
    "funciones_por_pelicula",
    "funciones_pelicula_por_multiplex",
    "editar_funcion",
    "eliminar_funcion",
]
