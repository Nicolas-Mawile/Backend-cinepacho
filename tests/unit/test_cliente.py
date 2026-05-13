import pytest
from app.infrastructure.models.cliente import Cliente
from datetime import datetime

def test_cliente_model_creacion(db_session):
    """Prueba la creación de un modelo Cliente en la base de datos."""
    nuevo_cliente = Cliente(
        nombre_completo="Juan Perez",
        correo="juan.perez@example.com",
        password_hash="hash_seguro_123",
        idioma_preferido="en"
    )
    
    db_session.add(nuevo_cliente)
    db_session.commit()
    db_session.refresh(nuevo_cliente)
    
    assert nuevo_cliente.id is not None
    assert nuevo_cliente.nombre_completo == "Juan Perez"
    assert nuevo_cliente.correo == "juan.perez@example.com"
    assert nuevo_cliente.password_hash == "hash_seguro_123"
    assert isinstance(nuevo_cliente.fecha_registro, datetime)
    assert nuevo_cliente.activo is True
    assert nuevo_cliente.puntos_acumulados == 0
    assert nuevo_cliente.idioma_preferido == "en"
