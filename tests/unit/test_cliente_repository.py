import pytest
from datetime import datetime, timedelta, timezone
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.repositories.cliente_repository import ClienteRepository

def test_repository_crear(db_session):
    repo = ClienteRepository(db_session)
    datos = {
        "nombre_completo": "Juan Perez",
        "correo": "juan@example.com",
        "password_hash": "hash123"
    }
    cliente = repo.crear(datos)
    
    assert cliente.id is not None
    assert cliente.nombre_completo == "Juan Perez"
    assert repo.exists(cliente.id)

def test_repository_buscar_por_correo(db_session):
    repo = ClienteRepository(db_session)
    cliente = Cliente(
        nombre_completo="Maria",
        correo="maria@example.com",
        password_hash="hash"
    )
    repo.add(cliente)
    
    encontrado = repo.buscar_por_correo("maria@example.com")
    assert encontrado is not None
    assert encontrado.id == cliente.id
    
    no_encontrado = repo.buscar_por_correo("no@existe.com")
    assert no_encontrado is None

def test_repository_actualizar_puntos(db_session):
    repo = ClienteRepository(db_session)
    cliente = Cliente(
        nombre_completo="Puntos",
        correo="puntos@example.com",
        password_hash="hash",
        puntos_acumulados=10
    )
    repo.add(cliente)
    
    repo.actualizar_puntos(cliente.id, 5)
    assert cliente.puntos_acumulados == 15
    
    repo.actualizar_puntos(cliente.id, -3)
    assert cliente.puntos_acumulados == 12

def test_repository_gestion_intentos_y_bloqueo(db_session):
    repo = ClienteRepository(db_session)
    correo = "bloqueo@example.com"
    cliente = Cliente(
        nombre_completo="Bloqueo",
        correo=correo,
        password_hash="hash"
    )
    repo.add(cliente)
    
    # 4 intentos fallidos -> No bloqueado
    for _ in range(4):
        repo.registrar_intento_fallido(correo)
    
    assert cliente.intentos_fallidos == 4
    assert repo.verificar_bloqueo(correo) is False
    
    # 5to intento -> Bloqueado
    repo.registrar_intento_fallido(correo)
    assert cliente.intentos_fallidos == 5
    assert repo.verificar_bloqueo(correo) is True
    assert cliente.bloqueado_hasta is not None
    
    # Reset
    repo.reset_intentos(correo)
    assert cliente.intentos_fallidos == 0
    assert cliente.bloqueado_hasta is None
    assert repo.verificar_bloqueo(correo) is False

def test_repository_autodesbloqueo(db_session):
    repo = ClienteRepository(db_session)
    correo = "auto@example.com"
    cliente = Cliente(
        nombre_completo="Auto",
        correo=correo,
        password_hash="hash",
        intentos_fallidos=5,
        bloqueado_hasta=datetime.now(timezone.utc) - timedelta(minutes=1)
    )
    repo.add(cliente)
    
    # Al verificar bloqueo, si el tiempo pasó, debe resetear e indicar False
    is_bloqueado = repo.verificar_bloqueo(correo)
    assert is_bloqueado is False
    assert cliente.intentos_fallidos == 0
    assert cliente.bloqueado_hasta is None
