"""Unit tests for auth service."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone
from app.domain.services.auth_service import authenticate_user

@pytest.mark.asyncio
async def test_login_exitoso():
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    repo = AsyncMock()
    repo.get_by_correo.return_value = MagicMock(
        id=1,
        password_hash=pwd_context.hash("password123"),
        intentos_fallidos=0,
        ultimo_intento=None,
    )
    repo.esta_bloqueado.return_value = False
    repo.reset_intentos.return_value = None

    tokens, error = await authenticate_user("test@example.com", "password123", repo)

    assert error is None
    assert "access_token" in tokens
    assert "refresh_token" in tokens

@pytest.mark.asyncio
async def test_login_password_incorrecto():
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    repo = AsyncMock()
    repo.get_by_correo.return_value = MagicMock(
        id=1,
        password_hash=pwd_context.hash("password123"),
        intentos_fallidos=0,
        ultimo_intento=None,
    )
    repo.esta_bloqueado.return_value = False

    tokens, error = await authenticate_user("test@example.com", "wrongpassword", repo)

    assert tokens is None
    assert error == "credenciales_invalidas"
    repo.incrementar_intentos.assert_called_once()

@pytest.mark.asyncio
async def test_login_usuario_no_existe():
    repo = AsyncMock()
    repo.get_by_correo.return_value = None

    tokens, error = await authenticate_user("noexiste@example.com", "password123", repo)

    assert tokens is None
    assert error == "credenciales_invalidas"

@pytest.mark.asyncio
async def test_login_cuenta_bloqueada():
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    repo = AsyncMock()
    repo.get_by_correo.return_value = MagicMock(
        id=1,
        password_hash=pwd_context.hash("password123"),
        intentos_fallidos=5,
        ultimo_intento=datetime.now(timezone.utc)
    )
    repo.esta_bloqueado.return_value = True

    tokens, error = await authenticate_user("bloqueado@example.com", "password123", repo)

    assert tokens is None
    assert "bloqueado" in error