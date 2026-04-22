# tests/unit/test_multiplex_repository.py
import pytest
import pytest_asyncio
import uuid
from decimal import Decimal
from app.models.multiplex import Multiplex
from app.infrastructure.repositories.multiplex_repository import MultiplexRepository


@pytest.fixture
def repo(db_session):
    """Instancia del repositorio."""
    return MultiplexRepository(db_session)


def multiplex_data(**kwargs):
    """Factory para crear datos de Multiplex."""
    defaults = {
        "id": str(uuid.uuid4()),
        "nombre": "Titán Plaza",
        "codigo": "TIT",
        "ciudad": "Bogotá",
        "direccion": "Calle 129B #71B-40",
        "latitud": Decimal("4.663100"),
        "longitud": Decimal("-74.150300"),
        "activo": True,
    }
    return Multiplex(**{**defaults, **kwargs})


@pytest.mark.asyncio
async def test_crear_multiplex(repo):
    """Test creación de multiplex."""
    mx = multiplex_data()
    creado = await repo.crear(mx)
    assert creado.id is not None
    assert creado.nombre == "Titán Plaza"


@pytest.mark.asyncio
async def test_listar_todos(repo):
    """Test listar todos los multiplexes."""
    await repo.crear(multiplex_data(id=str(uuid.uuid4()), codigo="TIT"))
    await repo.crear(multiplex_data(id=str(uuid.uuid4()), codigo="UNI", nombre="Unicentro"))
    result = await repo.listar()
    assert len(result) == 2


@pytest.mark.asyncio
async def test_listar_filtrar_ciudad(repo):
    """Test filtrar por ciudad."""
    await repo.crear(multiplex_data(id=str(uuid.uuid4()), codigo="TIT", ciudad="Bogotá"))
    await repo.crear(multiplex_data(id=str(uuid.uuid4()), codigo="MED", ciudad="Medellín"))
    result = await repo.listar(ciudad="Bogotá")
    assert len(result) == 1
    assert result[0].ciudad == "Bogotá"


@pytest.mark.asyncio
async def test_tiene_dependencias_sin_salas(repo):
    """Test verificar dependencias sin salas."""
    mx = await repo.crear(multiplex_data())
    assert await repo.tiene_dependencias(mx.id) is False


@pytest.mark.asyncio
async def test_desactivar(repo):
    """Test desactivar multiplex."""
    mx = await repo.crear(multiplex_data())
    desactivado = await repo.desactivar(mx.id)
    assert desactivado.activo is False