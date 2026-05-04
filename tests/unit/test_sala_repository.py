"""Tests unitarios para SalaRepository."""

import pytest
from app.infrastructure.models.sala import Sala
from app.infrastructure.repositories.sala_repository import SalaRepository


@pytest.fixture
def repo(db_session):
    """Instancia del repositorio de salas."""
    return SalaRepository(db_session)


@pytest.fixture
def multiplex_id():
    """ID de multiplex para usar en tests."""
    from app.infrastructure.models.multiplex import Multiplex
    
    multiplex = Multiplex(
        codigo="TST",
        nombre="Test Multiplex",
        ciudad="Test City",
        direccion="Test Direction",
        latitud=0.0,
        longitud=0.0,
    )
    from app.database import SessionLocal
    db = SessionLocal()
    db.add(multiplex)
    db.commit()
    multiplex_id_val = multiplex.id
    db.close()
    return multiplex_id_val


def test_crear_sala(repo, multiplex_id):
    """Test crear una sala."""
    sala = Sala(
        numero=1,
        capacidadTotal=150,
        capacidadPreferencial=20,
        multiplexId=multiplex_id,
        estaActiva=True,
    )
    creada = repo.add(sala)
    assert creada.id is not None
    assert creada.numero == 1
    assert creada.estaActiva is True


def test_obtener_sala(repo, multiplex_id):
    """Test obtener una sala por ID."""
    sala = Sala(
        numero=2,
        capacidadTotal=120,
        capacidadPreferencial=15,
        multiplexId=multiplex_id,
    )
    creada = repo.add(sala)
    obtenida = repo.get(creada.id)
    assert obtenida is not None
    assert obtenida.numero == 2


def test_obtener_sala_inexistente(repo):
    """Test obtener una sala que no existe."""
    obtenida = repo.get(99999)
    assert obtenida is None


def test_contar_por_multiplex(repo, multiplex_id):
    """Test contar salas por multiplex."""
    # Agregar 3 salas
    for i in range(1, 4):
        sala = Sala(
            numero=i,
            capacidadTotal=100,
            capacidadPreferencial=10,
            multiplexId=multiplex_id,
        )
        repo.add(sala)
    
    cantidad = repo.contar_por_multiplex(multiplex_id)
    assert cantidad == 3


def test_obtener_por_multiplex(repo, multiplex_id):
    """Test obtener salas por multiplex."""
    # Agregar 2 salas
    for i in range(1, 3):
        sala = Sala(
            numero=i,
            capacidadTotal=100,
            capacidadPreferencial=10,
            multiplexId=multiplex_id,
        )
        repo.add(sala)
    
    salas = repo.obtener_por_multiplex(multiplex_id)
    assert len(salas) == 2


def test_obtener_por_numero(repo, multiplex_id):
    """Test obtener sala por número."""
    sala = Sala(
        numero=42,
        capacidadTotal=200,
        capacidadPreferencial=30,
        multiplexId=multiplex_id,
    )
    repo.add(sala)
    
    obtenida = repo.obtener_por_numero(42, multiplex_id)
    assert obtenida is not None
    assert obtenida.numero == 42


def test_obtener_por_numero_inexistente(repo):
    """Test obtener sala por número que no existe."""
    obtenida = repo.obtener_por_numero(999, multiplex_id)
    assert obtenida is None


def test_actualizar_sala(repo, multiplex_id):
    """Test actualizar una sala."""
    sala = Sala(
        numero=5,
        capacidadTotal=100,
        capacidadPreferencial=10,
        multiplexId=multiplex_id,
    )
    creada = repo.add(sala)
    
    actualizada = repo.update(creada.id, {
        "capacidadTotal": 150,
        "capacidadPreferencial": 25,
    })
    
    assert actualizada.capacidadTotal == 150
    assert actualizada.capacidadPreferencial == 25


def test_desactivar_sala(repo, multiplex_id):
    """Test desactivar una sala."""
    sala = Sala(
        numero=7,
        capacidadTotal=100,
        capacidadPreferencial=10,
        multiplexId=multiplex_id,
        estaActiva=True,
    )
    creada = repo.add(sala)
    
    desactivada = repo.desactivar(creada.id)
    assert desactivada.estaActiva is False


def test_activar_sala(repo, multiplex_id):
    """Test activar una sala."""
    sala = Sala(
        numero=8,
        capacidadTotal=100,
        capacidadPreferencial=10,
        multiplexId=multiplex_id,
        estaActiva=False,
    )
    creada = repo.add(sala)
    
    activada = repo.activar(creada.id)
    assert activada.estaActiva is True


def test_eliminar_sala(repo, multiplex_id):
    """Test eliminar una sala."""
    sala = Sala(
        numero=9,
        capacidadTotal=100,
        capacidadPreferencial=10,
        multiplexId=multiplex_id,
    )
    creada = repo.add(sala)
    sala_id = creada.id
    
    eliminada = repo.delete(sala_id)
    assert eliminada is True
    
    obtenida = repo.get(sala_id)
    assert obtenida is None


def test_existe_sala(repo, multiplex_id):
    """Test verificar existencia de sala."""
    sala = Sala(
        numero=10,
        capacidadTotal=100,
        capacidadPreferencial=10,
        multiplexId=multiplex_id,
    )
    creada = repo.add(sala)
    
    existe = repo.exists(creada.id)
    assert existe is True
    
    no_existe = repo.exists(99999)
    assert no_existe is False


def test_paginacion_salas(repo, multiplex_id):
    """Test paginación al obtener salas."""
    # Agregar 5 salas
    for i in range(1, 6):
        sala = Sala(
            numero=i,
            capacidadTotal=100,
            capacidadPreferencial=10,
            multiplexId=multiplex_id,
        )
        repo.add(sala)
    
    # Primera página
    salas_p1 = repo.obtener_por_multiplex(multiplex_id, skip=0, limit=2)
    assert len(salas_p1) == 2
    
    # Segunda página
    salas_p2 = repo.obtener_por_multiplex(multiplex_id, skip=2, limit=2)
    assert len(salas_p2) == 2
    
    # Tercera página (1 sala)
    salas_p3 = repo.obtener_por_multiplex(multiplex_id, skip=4, limit=2)
    assert len(salas_p3) == 1
