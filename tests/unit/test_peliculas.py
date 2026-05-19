"""Unit tests for peliculas endpoints."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.api.v1.peliculas import (
    listar_peliculas, obtener_pelicula,
    crear_pelicula, actualizar_pelicula, desactivar_pelicula
)
from app.infrastructure.models.pelicula import Pelicula


def make_pelicula(**kwargs):
    p = Pelicula()
    p.id = kwargs.get("id", 1)
    p.titulo = kwargs.get("titulo", "Test Movie")
    p.duracionMinutos = kwargs.get("duracionMinutos", 120)
    p.linkTrailer = kwargs.get("linkTrailer", None)
    p.linkPoster = kwargs.get("linkPoster", None)
    p.sinopsis = kwargs.get("sinopsis", None)
    p.estaActiva = kwargs.get("estaActiva", True)
    return p


def test_listar_peliculas():
    db = MagicMock()
    db.execute.return_value.scalars.return_value.all.return_value = [make_pelicula()]
    result = listar_peliculas(db=db)
    assert len(result) == 1


def test_obtener_pelicula_exitoso():
    db = MagicMock()
    db.get.return_value = make_pelicula(id=1)
    result = obtener_pelicula(id=1, db=db)
    assert result.id == 1
    assert result.titulo == "Test Movie"


def test_obtener_pelicula_no_existe():
    db = MagicMock()
    db.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        obtener_pelicula(id=99, db=db)
    assert exc.value.status_code == 404


def test_crear_pelicula():
    from app.api.v1.peliculas import PeliculaCreate
    db = MagicMock()
    data = PeliculaCreate(titulo="Nueva Pelicula", duracionMinutos=100)
    result = crear_pelicula(data=data, db=db, _=None)
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_actualizar_pelicula_exitoso():
    from app.api.v1.peliculas import PeliculaUpdate
    db = MagicMock()
    db.get.return_value = make_pelicula(id=1)
    data = PeliculaUpdate(titulo="Titulo Actualizado")
    result = actualizar_pelicula(id=1, data=data, db=db, _=None)
    assert result.titulo == "Titulo Actualizado"


def test_actualizar_pelicula_no_existe():
    from app.api.v1.peliculas import PeliculaUpdate
    db = MagicMock()
    db.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        actualizar_pelicula(id=99, data=PeliculaUpdate(), db=db, _=None)
    assert exc.value.status_code == 404


def test_desactivar_pelicula_exitoso():
    db = MagicMock()
    db.get.return_value = make_pelicula(estaActiva=True)
    result = desactivar_pelicula(id=1, db=db, _=None)
    assert result["mensaje"] == "Película desactivada correctamente"


def test_desactivar_pelicula_ya_desactivada():
    db = MagicMock()
    db.get.return_value = make_pelicula(estaActiva=False)
    with pytest.raises(HTTPException) as exc:
        desactivar_pelicula(id=1, db=db, _=None)
    assert exc.value.status_code == 400


def test_desactivar_pelicula_no_existe():
    db = MagicMock()
    db.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        desactivar_pelicula(id=99, db=db, _=None)
    assert exc.value.status_code == 404