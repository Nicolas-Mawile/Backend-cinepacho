"""Integration tests for auth endpoints."""
import pytest
import jwt
import bcrypt
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.infrastructure.models.cliente import Cliente
from sqlalchemy import select

client = TestClient(app)

def test_registro_exitoso(db_session):
    """ST-06: test_registro_exitoso (status 201, token en response)"""
    payload = {
        "nombre": "Juan Perez",
        "correo": "juan@example.com",
        "password": "Password123",
        "confirm_password": "Password123"
    }
    response = client.post("/api/v1/auth/registro", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["cliente"]["correo"] == "juan@example.com"

def test_correo_duplicado_retorna_409(db_session):
    """ST-06: test_correo_duplicado_retorna_409"""
    payload = {
        "nombre": "Original",
        "correo": "duplicado@example.com",
        "password": "Password123",
        "confirm_password": "Password123"
    }
    # Primer registro
    client.post("/api/v1/auth/registro", json=payload)
    
    # Segundo registro con mismo correo
    response = client.post("/api/v1/auth/registro", json=payload)
    
    assert response.status_code == 409
    assert "registrado" in response.json()["detail"].lower()

def test_password_sin_mayuscula_retorna_422(db_session):
    """ST-06: test_password_sin_mayuscula_retorna_422"""
    payload = {
        "nombre": "Test",
        "correo": "nomayus@example.com",
        "password": "password123", # Sin mayúscula
        "confirm_password": "password123"
    }
    response = client.post("/api/v1/auth/registro", json=payload)
    assert response.status_code == 422
    assert any("mayúscula" in err["msg"] for err in response.json()["detail"])

def test_password_corta_retorna_422(db_session):
    """ST-06: test_password_corta_retorna_422"""
    payload = {
        "nombre": "Test",
        "correo": "short@example.com",
        "password": "P1", # Muy corta
        "confirm_password": "P1"
    }
    response = client.post("/api/v1/auth/registro", json=payload)
    assert response.status_code == 422

def test_passwords_no_coinciden_retorna_422(db_session):
    """ST-06: test_passwords_no_coinciden_retorna_422"""
    payload = {
        "nombre": "Test",
        "correo": "mismatch@example.com",
        "password": "Password123",
        "confirm_password": "OtherPassword123"
    }
    response = client.post("/api/v1/auth/registro", json=payload)
    assert response.status_code == 422
    assert any("no coinciden" in err["msg"] for err in response.json()["detail"])

def test_jwt_valido_decodificable(db_session):
    """ST-06: test_jwt_valido_decodificable"""
    payload = {
        "nombre": "JWT User",
        "correo": "jwt@example.com",
        "password": "Password123",
        "confirm_password": "Password123"
    }
    response = client.post("/api/v1/auth/registro", json=payload)
    token = response.json()["access_token"]
    
    # Decodificar y verificar claims
    decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert decoded["email"] == "jwt@example.com"
    assert "sub" in decoded

def test_hash_password_no_es_texto_plano(db_session):
    """ST-06: test_hash_password_no_es_texto_plano"""
    password_plana = "Password123Secret"
    payload = {
        "nombre": "Hash User",
        "correo": "hash@example.com",
        "password": password_plana,
        "confirm_password": password_plana
    }
    client.post("/api/v1/auth/registro", json=payload)
    
    # Buscar en la BD directamente
    stmt = select(Cliente).where(Cliente.correo == "hash@example.com")
    cliente = db_session.execute(stmt).scalar_one()
    
    assert cliente.password_hash != password_plana
    # Verificar que sea un hash bcrypt válido
    assert bcrypt.checkpw(password_plana.encode('utf-8')[:72], cliente.password_hash.encode('utf-8'))


# Tests de login
def test_login_exitoso(cliente_normal):
    """Test login exitoso con cliente existente"""
    response = client.post("/api/v1/login", json={
        "correo": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_fallido(cliente_normal):
    """Test login fallido con contraseña incorrecta"""
    response = client.post("/api/v1/login", json={
        "correo": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "credenciales" in response.json()["detail"].lower() or "incorrecto" in response.json()["detail"].lower()


def test_login_bloqueado(cliente_bloqueado):
    """Test login bloqueado"""
    response = client.post("/api/v1/login", json={
        "correo": "bloqueado@example.com",
        "password": "password123"
    })
    assert response.status_code in [429, 403]


def test_login_usuario_no_existe():
    """Test login con usuario que no existe"""
    response = client.post("/api/v1/login", json={
        "correo": "noexiste@example.com",
        "password": "password123"
    })
    assert response.status_code == 401


def test_refresh_token_exitoso(cliente_normal):
    """Test refresh de token exitoso"""
    # Primero hacer login para obtener tokens
    login_response = client.post("/api/v1/login", json={
        "correo": "test@example.com",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]

    response = client.post("/api/v1/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_token_reutilizado_retorna_401(cliente_normal):
    """Test que refresh token reutilizado retorna error"""
    login_response = client.post("/api/v1/login", json={
        "correo": "test@example.com",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]

    # Primer uso — válido
    client.post("/api/v1/refresh", json={"refresh_token": refresh_token})

    # Segundo uso — debe retornar 401
    response = client.post("/api/v1/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401
