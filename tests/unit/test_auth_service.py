"""Unit tests for auth service."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from app.domain.services.auth_service import authenticate_user

@pytest.mark.asyncio
async def test_login_exitoso():
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    repo = AsyncMock()
    repo.buscar_por_correo.return_value = MagicMock(
        id=1,
        password_hash=pwd_context.hash("password123"),
        intentos_fallidos=0,
        ultimo_intento=None,
    )
    repo.verificar_bloqueo.return_value = False

    tokens, error = await authenticate_user("test@example.com", "password123", repo)

    assert error is None
    assert "access_token" in tokens
    assert "refresh_token" in tokens

@pytest.mark.asyncio
async def test_login_password_incorrecto():
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    cliente_mock = MagicMock(
        id=1,
        password_hash=pwd_context.hash("password123"),
        intentos_fallidos=0,
    )
    repo = AsyncMock()
    repo.buscar_por_correo.return_value = cliente_mock
    repo.verificar_bloqueo.return_value = False
    repo.buscar_por_correo.side_effect = None
    # Segunda llamada tras registrar intento devuelve intentos=1
    repo.buscar_por_correo.side_effect = [cliente_mock, MagicMock(intentos_fallidos=1)]

    tokens, error = await authenticate_user("test@example.com", "wrongpassword", repo)

    assert tokens is None
    assert error == "credenciales_invalidas"
    repo.registrar_intento_fallido.assert_called_once_with("test@example.com")

@pytest.mark.asyncio
async def test_login_usuario_no_existe():
    repo = AsyncMock()
    repo.buscar_por_correo.return_value = None

    tokens, error = await authenticate_user("noexiste@example.com", "password123", repo)

    assert tokens is None
    assert error == "credenciales_invalidas"

@pytest.mark.asyncio
async def test_login_cuenta_bloqueada():
    repo = AsyncMock()
    repo.buscar_por_correo.return_value = MagicMock(
        id=1,
        intentos_fallidos=5,
        ultimo_intento=datetime.now(timezone.utc),
    )
    repo.verificar_bloqueo.return_value = True

    tokens, error = await authenticate_user("bloqueado@example.com", "password123", repo)

    assert tokens is None
    assert "bloqueado" in error