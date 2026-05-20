"""Unit tests for funciones and cartelera endpoints."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from datetime import datetime, timedelta


# ── CARTELERA ─────────────────────────────────────────────────────────────────

def test_ver_cartelera_multiplex_no_existe():
    from app.api.v1.cartelera import ver_cartelera
    db = MagicMock()
    db.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        ver_cartelera(multiplex_id=99, db=db)
    assert exc.value.status_code == 404


def test_ver_cartelera_exitoso():
    from app.api.v1.cartelera import ver_cartelera
    from app.infrastructure.models.multiplex import Multiplex
    db = MagicMock()
    db.get.return_value = Multiplex()
    db.execute.return_value.scalars.return_value.all.return_value = []
    result = ver_cartelera(multiplex_id=1, db=db)
    assert result == []


def test_agregar_cartelera_multiplex_no_existe():
    from app.api.v1.cartelera import agregar_a_cartelera, CartelераAdd
    db = MagicMock()
    db.get.side_effect = [None]
    with pytest.raises(HTTPException) as exc:
        agregar_a_cartelera(multiplex_id=99, data=CartelераAdd(peliculaId=1), db=db, _=None)
    assert exc.value.status_code == 404


def test_agregar_cartelera_pelicula_no_existe():
    from app.api.v1.cartelera import agregar_a_cartelera, CartelераAdd
    from app.infrastructure.models.multiplex import Multiplex
    db = MagicMock()
    db.get.side_effect = [Multiplex(), None]
    with pytest.raises(HTTPException) as exc:
        agregar_a_cartelera(multiplex_id=1, data=CartelераAdd(peliculaId=99), db=db, _=None)
    assert exc.value.status_code == 404


def test_agregar_cartelera_pelicula_inactiva():
    from app.api.v1.cartelera import agregar_a_cartelera, CartelераAdd
    from app.infrastructure.models.multiplex import Multiplex
    from app.infrastructure.models.pelicula import Pelicula
    db = MagicMock()
    pelicula = Pelicula()
    pelicula.estaActiva = False
    db.get.side_effect = [Multiplex(), pelicula]
    with pytest.raises(HTTPException) as exc:
        agregar_a_cartelera(multiplex_id=1, data=CartelераAdd(peliculaId=1), db=db, _=None)
    assert exc.value.status_code == 400


def test_agregar_cartelera_duplicado():
    from app.api.v1.cartelera import agregar_a_cartelera, CartelераAdd
    from app.infrastructure.models.multiplex import Multiplex
    from app.infrastructure.models.pelicula import Pelicula
    from app.infrastructure.models.multiplex_cartelera import MultiplexCartelera
    db = MagicMock()
    pelicula = Pelicula()
    pelicula.estaActiva = True
    db.get.side_effect = [Multiplex(), pelicula]
    db.execute.return_value.scalar_one_or_none.return_value = MultiplexCartelera()
    with pytest.raises(HTTPException) as exc:
        agregar_a_cartelera(multiplex_id=1, data=CartelераAdd(peliculaId=1), db=db, _=None)
    assert exc.value.status_code == 409


def test_remover_cartelera_no_existe():
    from app.api.v1.cartelera import remover_de_cartelera
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = None
    with pytest.raises(HTTPException) as exc:
        remover_de_cartelera(multiplex_id=1, pelicula_id=99, db=db, _=None)
    assert exc.value.status_code == 404


def test_remover_cartelera_exitoso():
    from app.api.v1.cartelera import remover_de_cartelera
    from app.infrastructure.models.multiplex_cartelera import MultiplexCartelera
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = MultiplexCartelera()
    result = remover_de_cartelera(multiplex_id=1, pelicula_id=1, db=db, _=None)
    assert "removida" in result["mensaje"]


# ── FUNCIONES ─────────────────────────────────────────────────────────────────

def test_crear_funcion_sala_no_existe():
    from app.api.v1.funciones import crear_funcion, FuncionCreate
    db = MagicMock()
    db.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        crear_funcion(
            data=FuncionCreate(peliculaId=1, salaId=99, fechaHora=datetime.now()),
            db=db, _=None
        )
    assert exc.value.status_code == 404


def test_crear_funcion_pelicula_inactiva():
    from app.api.v1.funciones import crear_funcion, FuncionCreate
    from app.infrastructure.models.sala import Sala
    from app.infrastructure.models.pelicula import Pelicula
    db = MagicMock()
    sala = Sala()
    sala.estaActiva = True
    sala.multiplexId = 1
    pelicula = Pelicula()
    pelicula.estaActiva = False
    db.get.side_effect = [sala, pelicula]
    with pytest.raises(HTTPException) as exc:
        crear_funcion(
            data=FuncionCreate(peliculaId=1, salaId=1, fechaHora=datetime.now()),
            db=db, _=None
        )
    assert exc.value.status_code == 400


def test_crear_funcion_pelicula_no_en_cartelera():
    from app.api.v1.funciones import crear_funcion, FuncionCreate
    from app.infrastructure.models.sala import Sala
    from app.infrastructure.models.pelicula import Pelicula
    from app.infrastructure.repositories.funcion_repository import FuncionRepository
    db = MagicMock()
    sala = Sala()
    sala.estaActiva = True
    sala.multiplexId = 1
    pelicula = Pelicula()
    pelicula.estaActiva = True
    pelicula.duracionMinutos = 120
    db.get.side_effect = [sala, pelicula]
    with patch.object(FuncionRepository, 'pelicula_en_cartelera', return_value=False):
        with pytest.raises(HTTPException) as exc:
            crear_funcion(
                data=FuncionCreate(peliculaId=1, salaId=1, fechaHora=datetime.now()),
                db=db, _=None
            )
    assert exc.value.status_code == 400


def test_crear_funcion_solapamiento():
    from app.api.v1.funciones import crear_funcion, FuncionCreate
    from app.infrastructure.models.sala import Sala
    from app.infrastructure.models.pelicula import Pelicula
    from app.infrastructure.repositories.funcion_repository import FuncionRepository
    db = MagicMock()
    sala = Sala()
    sala.estaActiva = True
    sala.multiplexId = 1
    pelicula = Pelicula()
    pelicula.estaActiva = True
    pelicula.duracionMinutos = 120
    db.get.side_effect = [sala, pelicula]
    with patch.object(FuncionRepository, 'pelicula_en_cartelera', return_value=True), \
         patch.object(FuncionRepository, 'hay_solapamiento', return_value=True):
        with pytest.raises(HTTPException) as exc:
            crear_funcion(
                data=FuncionCreate(peliculaId=1, salaId=1, fechaHora=datetime.now()),
                db=db, _=None
            )
    assert exc.value.status_code == 409


def test_eliminar_funcion_no_existe():
    from app.api.v1.funciones import eliminar_funcion
    from app.infrastructure.repositories.funcion_repository import FuncionRepository
    db = MagicMock()
    with patch.object(FuncionRepository, 'get', return_value=None):
        with pytest.raises(HTTPException) as exc:
            eliminar_funcion(id=99, db=db, _=None)
    assert exc.value.status_code == 404


def test_eliminar_funcion_con_boletas():
    from app.api.v1.funciones import eliminar_funcion
    from app.infrastructure.models.funcion import Funcion
    from app.infrastructure.repositories.funcion_repository import FuncionRepository
    db = MagicMock()
    with patch.object(FuncionRepository, 'get', return_value=Funcion()), \
         patch.object(FuncionRepository, 'tiene_boletas', return_value=True):
        with pytest.raises(HTTPException) as exc:
            eliminar_funcion(id=1, db=db, _=None)
    assert exc.value.status_code == 409


def test_eliminar_funcion_exitoso():
    from app.api.v1.funciones import eliminar_funcion
    from app.infrastructure.models.funcion import Funcion
    from app.infrastructure.repositories.funcion_repository import FuncionRepository
    db = MagicMock()
    with patch.object(FuncionRepository, 'get', return_value=Funcion()), \
         patch.object(FuncionRepository, 'tiene_boletas', return_value=False), \
         patch.object(FuncionRepository, 'delete', return_value=True):
        result = eliminar_funcion(id=1, db=db, _=None)
    assert "eliminada" in result["mensaje"]