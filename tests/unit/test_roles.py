"""Unit tests for role-based access control."""
import pytest
from fastapi import HTTPException
from app.api.dependencies import (
    get_current_cajero, get_current_admin_mx,
    get_current_admin_general, get_current_cliente
)
from app.models.empleado import Empleado
from app.models.cliente import Cliente

@pytest.mark.asyncio
async def test_admin_general_accede_correctamente():
    empleado = Empleado(id=1, cargo="admin_general", activo=True)
    result = await get_current_admin_general(user=empleado)
    assert result.cargo == "admin_general"

@pytest.mark.asyncio
async def test_cajero_accede_correctamente():
    empleado = Empleado(id=2, cargo="cajero", activo=True)
    result = await get_current_cajero(user=empleado)
    assert result.cargo == "cajero"

@pytest.mark.asyncio
async def test_cajero_no_puede_ser_admin():
    empleado = Empleado(id=2, cargo="cajero", activo=True)
    with pytest.raises(HTTPException) as exc:
        await get_current_admin_general(user=empleado)
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_cliente_no_puede_acceder_a_endpoint_empleado():
    cliente = Cliente(id=1, correo="test@mail.com")
    with pytest.raises(HTTPException) as exc:
        await get_current_cajero(user=cliente)
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_admin_mx_no_puede_ser_admin_general():
    empleado = Empleado(id=3, cargo="admin_multiplex", activo=True)
    with pytest.raises(HTTPException) as exc:
        await get_current_admin_general(user=empleado)
    assert exc.value.status_code == 403