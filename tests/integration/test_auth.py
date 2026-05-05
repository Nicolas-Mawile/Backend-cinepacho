"""Integration tests for auth endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_registro_exitoso(db_session):
    """Prueba un registro de cliente exitoso."""
    payload = {
        "nombre": "Test User",
        "correo": "test@example.com",
        "password": "Password123",
        "confirm_password": "Password123"
    }
    response = client.post("/api/v1/auth/registro", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["cliente"]["correo"] == "test@example.com"
    assert data["cliente"]["nombre_completo"] == "Test User"

def test_correo_duplicado_409(db_session):
    """Prueba que no se permita registrar un correo ya existente."""
    payload = {
        "nombre": "User 1",
        "correo": "dup@example.com",
        "password": "Password123",
        "confirm_password": "Password123"
    }
    # Primer registro
    client.post("/api/v1/auth/registro", json=payload)
    
    # Segundo registro con mismo correo
    response = client.post("/api/v1/auth/registro", json=payload)
    
    assert response.status_code == 409
    assert response.json()["detail"] == "El correo electrónico ya está registrado"

def test_password_debil_422(db_session):
    """Prueba validaciones de complejidad de contraseña."""
    payload = {
        "nombre": "Test User",
        "correo": "weak@example.com",
        "password": "123", # Muy corta y sin mayúsculas/minúsculas
        "confirm_password": "123"
    }
    response = client.post("/api/v1/auth/registro", json=payload)
    assert response.status_code == 422

def test_passwords_no_coinciden_422(db_session):
    """Prueba que las contraseñas deban coincidir."""
    payload = {
        "nombre": "Test User",
        "correo": "mismatch@example.com",
        "password": "Password123",
        "confirm_password": "DifferentPassword123"
    }
    response = client.post("/api/v1/auth/registro", json=payload)
    assert response.status_code == 422
    # El detalle del error de pydantic debe mencionar que no coinciden
    errors = response.json()["detail"]
    assert any("no coinciden" in err["msg"] for err in errors)
