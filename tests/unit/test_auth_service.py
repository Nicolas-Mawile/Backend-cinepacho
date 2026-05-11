"""Unit tests for auth service."""
from datetime import datetime, timezone
from unittest.mock import MagicMock

from jose import jwt
from app.domain.services.auth_service import AuthService
from app.config import settings


def authenticate_user(email: str, password: str, repo):
    """Helper de pruebas para validar credenciales de usuario."""
    usuario = repo.buscar_por_correo(email)
    if usuario is None:
        return None, "credenciales_invalidas"

    if repo.verificar_bloqueo(email):
        return None, "bloqueado"

    auth_service = AuthService()
    if not auth_service.verifyPassword(password, usuario.password_hash):
        repo.registrar_intento_fallido(email)
        return None, "credenciales_invalidas"

    return {"access_token": "mock-token"}, None


def test_hash_password_and_verify():
    auth_service = AuthService()
    plain_password = "password123"

    hashed = auth_service.hashPassword(plain_password)
    assert auth_service.verifyPassword(plain_password, hashed)
    assert not auth_service.verifyPassword("wrongpass", hashed)

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