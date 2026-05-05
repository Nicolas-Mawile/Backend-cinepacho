"""Unit tests for auth service."""
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone
from app.domain.services.auth_service import authenticate_user

def test_login_exitoso():
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    repo = MagicMock()
    repo.buscar_por_correo.return_value = MagicMock(
        id=1,
        password_hash=pwd_context.hash("password123"),
        intentos_fallidos=0,
        ultimo_intento=None,
    )
    repo.verificar_bloqueo.return_value = False

    tokens, error = authenticate_user("test@example.com", "password123", repo)

    assert error is None
    assert "access_token" in tokens
    assert "refresh_token" in tokens

def test_login_password_incorrecto():
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    cliente_mock = MagicMock(
        id=1,
        password_hash=pwd_context.hash("password123"),
        intentos_fallidos=1,
    )
    repo = MagicMock()
    repo.buscar_por_correo.return_value = cliente_mock
    repo.verificar_bloqueo.return_value = False

    tokens, error = authenticate_user("test@example.com", "wrongpassword", repo)

    assert tokens is None
    assert error == "credenciales_invalidas"
    repo.registrar_intento_fallido.assert_called_once_with("test@example.com")

def test_login_usuario_no_existe():
    repo = MagicMock()
    repo.buscar_por_correo.return_value = None

    tokens, error = authenticate_user("noexiste@example.com", "password123", repo)

    assert tokens is None
    assert error == "credenciales_invalidas"

def test_login_cuenta_bloqueada():
    repo = MagicMock()
    repo.buscar_por_correo.return_value = MagicMock(
        id=1,
        intentos_fallidos=5,
        ultimo_intento=datetime.now(timezone.utc),
    )
    repo.verificar_bloqueo.return_value = True

    tokens, error = authenticate_user("bloqueado@example.com", "password123", repo)

    assert tokens is None
    assert "bloqueado" in error