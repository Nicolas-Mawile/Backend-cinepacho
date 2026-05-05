"""Unit tests for auth dependencies."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from app.api.dependencies import get_current_user, get_current_cliente, get_current_admin_general
from app.models.cliente import Cliente
from app.models.empleado import Empleado

@pytest.mark.asyncio
async def test_token_invalido_lanza_401():
    db = AsyncMock()
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token="token_invalido", db=db)
    assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_cliente_en_endpoint_admin_lanza_403():
    cliente = Cliente(id=1, nombre="Test", correo="test@mail.com")
    with pytest.raises(HTTPException) as exc:
        await get_current_admin_general(user=cliente)
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_get_current_cliente_con_empleado_lanza_403():
    empleado = Empleado(id=1, nombre="Emp", correo="emp@mail.com", rol="EMPLEADO-CAJERO")
    with pytest.raises(HTTPException) as exc:
        await get_current_cliente(user=empleado)
    assert exc.value.status_code == 403