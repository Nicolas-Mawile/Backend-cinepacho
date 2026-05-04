"""Tests unitarios para SalaService."""

import pytest
from app.infrastructure.models.sala import Sala
from app.infrastructure.models.multiplex import Multiplex
from app.domain.services.sala_service import SalaService
from app.domain.exceptions import (
    SalaNotFoundError,
    MultiplexNotFoundError,
    SalaLimitExceededError,
    DuplicateNumeroSalaError,
)
from app.api.schemas.sala import SalaCreate, SalaUpdate
from app.database import SessionLocal


@pytest.fixture
def multiplex():
    """Crea un multiplex de prueba."""
    db = SessionLocal()
    multiplex = Multiplex(
        codigo="TEST",
        nombre="Test Multiplex",
        ciudad="Test",
        direccion="Test Direction",
        latitud=0.0,
        longitud=0.0,
    )
    db.add(multiplex)
    db.commit()
    multiplex_id = multiplex.id
    db.close()
    return multiplex_id


@pytest.fixture
def service(db_session):
    """Instancia del servicio."""
    return SalaService(db_session)


def test_crear_sala_exitosa(service, multiplex):
    """Test crear una sala exitosamente."""
    datos = SalaCreate(numero=1, capacidadTotal=150, capacidadPreferencial=20)
    sala = service.crear_sala(multiplex, datos)
    
    assert sala.id is not None
    assert sala.numero == 1
    assert sala.estaActiva is True
    assert sala.multiplexId == multiplex


def test_crear_sala_multiplex_no_existe(service):
    """Test crear sala cuando multiplex no existe."""
    datos = SalaCreate(numero=1, capacidadTotal=150, capacidadPreferencial=20)
    
    with pytest.raises(MultiplexNotFoundError):
        service.crear_sala(99999, datos)


def test_crear_sala_numero_duplicado(service, multiplex):
    """Test crear sala con número duplicado."""
    datos1 = SalaCreate(numero=1, capacidadTotal=150, capacidadPreferencial=20)
    service.crear_sala(multiplex, datos1)
    
    datos2 = SalaCreate(numero=1, capacidadTotal=100, capacidadPreferencial=10)
    
    with pytest.raises(DuplicateNumeroSalaError):
        service.crear_sala(multiplex, datos2)


def test_validar_limite_salas(service, multiplex, db_session):
    """Test validar límite de salas por multiplex."""
    # Crear 10 salas (el máximo)
    for i in range(1, 11):
        datos = SalaCreate(numero=i, capacidadTotal=100, capacidadPreferencial=10)
        service.crear_sala(multiplex, datos)
    
    # Intentar crear la 11ª sala
    datos_extra = SalaCreate(numero=11, capacidadTotal=100, capacidadPreferencial=10)
    
    with pytest.raises(SalaLimitExceededError):
        service.crear_sala(multiplex, datos_extra)


def test_obtener_sala_exitosa(service, multiplex):
    """Test obtener una sala existente."""
    datos = SalaCreate(numero=5, capacidadTotal=100, capacidadPreferencial=10)
    creada = service.crear_sala(multiplex, datos)
    
    obtenida = service.obtener_sala(creada.id)
    assert obtenida.id == creada.id
    assert obtenida.numero == 5


def test_obtener_sala_no_existe(service):
    """Test obtener una sala que no existe."""
    with pytest.raises(SalaNotFoundError):
        service.obtener_sala(99999)


def test_obtener_salas_multiplex(service, multiplex):
    """Test obtener salas de un multiplex."""
    # Crear 3 salas
    for i in range(1, 4):
        datos = SalaCreate(numero=i, capacidadTotal=100, capacidadPreferencial=10)
        service.crear_sala(multiplex, datos)
    
    salas = service.obtener_salas_multiplex(multiplex)
    assert len(salas) == 3


def test_obtener_salas_multiplex_no_existe(service):
    """Test obtener salas de un multiplex que no existe."""
    with pytest.raises(MultiplexNotFoundError):
        service.obtener_salas_multiplex(99999)


def test_obtener_salas_multiplex_vacio(service, multiplex):
    """Test obtener salas de un multiplex sin salas."""
    salas = service.obtener_salas_multiplex(multiplex)
    assert len(salas) == 0


def test_actualizar_sala_exitosa(service, multiplex):
    """Test actualizar una sala."""
    datos = SalaCreate(numero=7, capacidadTotal=100, capacidadPreferencial=10)
    creada = service.crear_sala(multiplex, datos)
    
    actualizacion = SalaUpdate(capacidadTotal=200, capacidadPreferencial=30)
    actualizada = service.actualizar_sala(creada.id, actualizacion)
    
    assert actualizada.capacidadTotal == 200
    assert actualizada.capacidadPreferencial == 30


def test_actualizar_sala_numero_duplicado(service, multiplex):
    """Test actualizar sala a número que ya existe."""
    # Crear 2 salas
    datos1 = SalaCreate(numero=1, capacidadTotal=100, capacidadPreferencial=10)
    sala1 = service.crear_sala(multiplex, datos1)
    
    datos2 = SalaCreate(numero=2, capacidadTotal=100, capacidadPreferencial=10)
    sala2 = service.crear_sala(multiplex, datos2)
    
    # Intentar cambiar número de sala2 al de sala1
    actualizacion = SalaUpdate(numero=1)
    
    with pytest.raises(DuplicateNumeroSalaError):
        service.actualizar_sala(sala2.id, actualizacion)


def test_actualizar_sala_no_existe(service):
    """Test actualizar una sala que no existe."""
    actualizacion = SalaUpdate(capacidadTotal=200)
    
    with pytest.raises(SalaNotFoundError):
        service.actualizar_sala(99999, actualizacion)


def test_cambiar_estado_activo(service, multiplex):
    """Test cambiar estado de sala a inactivo."""
    datos = SalaCreate(numero=10, capacidadTotal=100, capacidadPreferencial=10)
    creada = service.crear_sala(multiplex, datos)
    assert creada.estaActiva is True
    
    desactivada = service.cambiar_estado(creada.id, False)
    assert desactivada.estaActiva is False


def test_cambiar_estado_inactivo_a_activo(service, multiplex):
    """Test cambiar estado de sala inactiva a activa."""
    datos = SalaCreate(numero=11, capacidadTotal=100, capacidadPreferencial=10)
    creada = service.crear_sala(multiplex, datos)
    service.cambiar_estado(creada.id, False)
    
    activada = service.cambiar_estado(creada.id, True)
    assert activada.estaActiva is True


def test_cambiar_estado_sala_no_existe(service):
    """Test cambiar estado de sala que no existe."""
    with pytest.raises(SalaNotFoundError):
        service.cambiar_estado(99999, False)


def test_eliminar_sala_exitosa(service, multiplex):
    """Test eliminar una sala exitosamente."""
    datos = SalaCreate(numero=15, capacidadTotal=100, capacidadPreferencial=10)
    creada = service.crear_sala(multiplex, datos)
    sala_id = creada.id
    
    eliminada = service.eliminar_sala(sala_id)
    assert eliminada is True
    
    # Verificar que ya no existe
    with pytest.raises(SalaNotFoundError):
        service.obtener_sala(sala_id)


def test_eliminar_sala_no_existe(service):
    """Test eliminar una sala que no existe."""
    eliminada = service.eliminar_sala(99999)
    assert eliminada is False


def test_validar_numero_unico(service):
    """Test validación de número único."""
    # Crear sala con número 42
    db = SessionLocal()
    sala1 = Sala(numero=42, capacidadTotal=100, capacidadPreferencial=10, multiplexId=1)
    db.add(sala1)
    db.commit()
    sala1_id = sala1.id
    db.close()
    
    # Validar que número 42 no es único
    with pytest.raises(DuplicateNumeroSalaError):
        service.validar_numero_unico(42)
    
    # Validar que número 42 es único si excluimos sala1
    service.validar_numero_unico(42, excluir_sala_id=sala1_id)


def test_paginacion_salas(service, multiplex):
    """Test paginación al obtener salas de multiplex."""
    # Crear 5 salas
    for i in range(1, 6):
        datos = SalaCreate(numero=i, capacidadTotal=100, capacidadPreferencial=10)
        service.crear_sala(multiplex, datos)
    
    # Primera página
    salas_p1 = service.obtener_salas_multiplex(multiplex, skip=0, limit=2)
    assert len(salas_p1) == 2
    
    # Segunda página
    salas_p2 = service.obtener_salas_multiplex(multiplex, skip=2, limit=2)
    assert len(salas_p2) == 2
    
    # Tercera página
    salas_p3 = service.obtener_salas_multiplex(multiplex, skip=4, limit=2)
    assert len(salas_p3) == 1
