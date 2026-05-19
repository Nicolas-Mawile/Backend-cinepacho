"""Unit tests for new app.api funciones and cartelera endpoints."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.cartelera import (
    ver_cartelera_general,
    agregar_a_cartelera_general,
    remover_de_cartelera_general,
)
from app.api.funciones import (
    funciones_por_pelicula,
    funciones_pelicula_por_multiplex,
    editar_funcion,
)
from app.api.schemas.cartelera import CarteleraAdd
from app.api.schemas.funcion import FuncionUpdate
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.multiplex_cartelera import MultiplexCartelera
from app.infrastructure.models.pelicula import Pelicula
from app.infrastructure.models.sala import Sala
from app.infrastructure.repositories.funcion_repository import FuncionRepository


def _exec_with_scalars_list(values):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = values
    return mock_result


# CARTELERA GENERAL

def test_ver_cartelera_general_exitoso():
    db = MagicMock()
    db.execute.return_value.scalars.return_value.all.return_value = []

    result = ver_cartelera_general(db=db)

    assert result == []


def test_agregar_cartelera_general_sin_multiplex_activos():
    db = MagicMock()
    pelicula = Pelicula()
    pelicula.estaActiva = True
    db.get.return_value = pelicula
    db.execute.side_effect = [_exec_with_scalars_list([])]

    with pytest.raises(HTTPException) as exc:
        agregar_a_cartelera_general(data=CarteleraAdd(peliculaId=1), db=db, _=None)

    assert exc.value.status_code == 404


def test_agregar_cartelera_general_exitoso():
    db = MagicMock()
    pelicula = Pelicula()
    pelicula.estaActiva = True
    db.get.return_value = pelicula
    db.execute.side_effect = [
        _exec_with_scalars_list([1, 2]),
        _exec_with_scalars_list([2]),
    ]

    result = agregar_a_cartelera_general(data=CarteleraAdd(peliculaId=5), db=db, _=None)

    assert result["multiplexesActualizados"] == 1
    assert result["multiplexesSinCambio"] == 1
    db.add_all.assert_called_once()
    db.commit.assert_called_once()


def test_remover_de_cartelera_general_no_existe():
    db = MagicMock()
    db.execute.return_value.scalars.return_value.all.return_value = []

    with pytest.raises(HTTPException) as exc:
        remover_de_cartelera_general(pelicula_id=9, db=db, _=None)

    assert exc.value.status_code == 404


def test_remover_de_cartelera_general_exitoso():
    db = MagicMock()
    db.execute.return_value.scalars.return_value.all.return_value = [
        MultiplexCartelera(),
        MultiplexCartelera(),
    ]

    result = remover_de_cartelera_general(pelicula_id=9, db=db, _=None)

    assert result["multiplexesAfectados"] == 2
    assert db.delete.call_count == 2
    db.commit.assert_called_once()


# FUNCIONES POR PELICULA

def test_funciones_por_pelicula_pelicula_no_existe():
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        funciones_por_pelicula(pelicula_id=404, db=db)

    assert exc.value.status_code == 404


def test_funciones_pelicula_por_multiplex_multiplex_no_existe():
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        funciones_pelicula_por_multiplex(multiplex_id=404, pelicula_id=1, db=db)

    assert exc.value.status_code == 404


def test_funciones_pelicula_por_multiplex_exitoso():
    from app.infrastructure.models.multiplex import Multiplex

    db = MagicMock()
    db.get.side_effect = [Multiplex(), Pelicula()]
    db.execute.return_value.scalars.return_value.all.return_value = []

    result = funciones_pelicula_por_multiplex(multiplex_id=1, pelicula_id=1, db=db)

    assert result == []


# EDITAR FUNCION

def test_editar_funcion_con_dependencias():
    db = MagicMock()
    funcion = Funcion()

    with patch.object(FuncionRepository, "get", return_value=funcion), patch.object(
        FuncionRepository, "tiene_boletas", return_value=True
    ):
        with pytest.raises(HTTPException) as exc:
            editar_funcion(id=1, data=FuncionUpdate(), db=db, _=None)

    assert exc.value.status_code == 409


def test_editar_funcion_exitoso():
    db = MagicMock()
    inicio = datetime(2026, 5, 20, 15, 0, 0)
    funcion = Funcion()
    funcion.salaId = 1
    funcion.peliculaId = 2
    funcion.fechaHora = inicio

    sala = Sala()
    sala.estaActiva = True
    sala.multiplexId = 7

    pelicula = Pelicula()
    pelicula.estaActiva = True
    pelicula.duracionMinutos = 120

    db.get.side_effect = [sala, pelicula]

    with patch.object(FuncionRepository, "get", return_value=funcion), patch.object(
        FuncionRepository, "tiene_boletas", return_value=False
    ), patch.object(
        FuncionRepository, "pelicula_en_cartelera", return_value=True
    ), patch.object(
        FuncionRepository, "hay_solapamiento", return_value=False
    ), patch.object(
        FuncionRepository, "update", return_value=funcion
    ) as mock_update:
        editar_funcion(id=1, data=FuncionUpdate(fechaHora=inicio), db=db, _=None)

    cambios = mock_update.call_args[0][1]
    assert cambios["fechaHora"] == inicio
    assert cambios["fechaHoraFin"] == inicio + timedelta(minutes=120)
