import pytest
from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.repositories.multiplex_repository import MultiplexRepository


@pytest.fixture
def repo(db_session):
    """Instancia del repositorio."""
    return MultiplexRepository(db_session)


def multiplex_data(**kwargs):
    """Factory para crear datos de Multiplex."""
    defaults = {
        "nombre": "Titán Plaza",
        "codigo": "TIT",
        "ciudad": "Bogotá",
        "direccion": "Calle 129B #71B-40",
        "latitud": 4.6631,
        "longitud": -74.1503,
        "estaActivo": True,
    }
    return Multiplex(**{**defaults, **kwargs})


def test_crear_multiplex(repo):
    """Test creación de multiplex."""
    mx = multiplex_data()
    creado = repo.crear(mx)
    assert creado.id is not None
    assert creado.nombre == "Titán Plaza"


def test_listar_todos(repo):
    """Test listar todos los multiplexes."""
    repo.crear(multiplex_data(codigo="TIT"))
    repo.crear(multiplex_data(codigo="UNI", nombre="Unicentro"))
    result = repo.listar()
    assert len(result) == 2


def test_listar_filtrar_ciudad(repo):
    """Test filtrar por ciudad."""
    repo.crear(multiplex_data(codigo="TIT", ciudad="Bogotá"))
    repo.crear(multiplex_data(codigo="MED", ciudad="Medellín"))
    result = repo.listar(ciudad="Bogotá")
    assert len(result) == 1
    assert result[0].ciudad == "Bogotá"


def test_tiene_dependencias_sin_salas(repo):
    """Test verificar dependencias sin salas."""
    mx = repo.crear(multiplex_data())
    assert repo.tiene_dependencias(mx.id) is False


def test_desactivar(repo):
    """Test desactivar multiplex."""
    mx = repo.crear(multiplex_data())
    desactivado = repo.desactivar(mx.id)
    assert desactivado.activo is False