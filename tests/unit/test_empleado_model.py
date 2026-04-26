"""Unit tests for Empleado model."""
import pytest
from app.models.empleado import Empleado

def test_cajero_tiene_multiplex():
    empleado = Empleado(
        codigo_empleado="EMP-001",
        nombre="Juan Cajero",
        correo="cajero@cinepacho.com",
        password_hash="hash",
        cargo="cajero",
        multiplex_id=1,
        activo=True,
    )
    assert empleado.multiplex_id is not None
    assert empleado.cargo == "cajero"

def test_admin_general_sin_multiplex():
    empleado = Empleado(
        codigo_empleado="EMP-003",
        nombre="Carlos Admin",
        correo="admin@cinepacho.com",
        password_hash="hash",
        cargo="admin_general",
        multiplex_id=None,
        activo=True,
    )
    assert empleado.multiplex_id is None
    assert empleado.cargo == "admin_general"

def test_codigo_empleado_asignado():
    empleado = Empleado(
        codigo_empleado="EMP-999",
        nombre="Test",
        correo="test@cinepacho.com",
        password_hash="hash",
        cargo="cajero",
        multiplex_id=1,
    )
    assert empleado.codigo_empleado == "EMP-999"