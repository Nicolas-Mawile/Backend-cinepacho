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
