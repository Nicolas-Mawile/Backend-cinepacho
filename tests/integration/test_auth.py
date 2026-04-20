"""Integration tests for auth endpoints."""
import pytest

@pytest.mark.asyncio
async def test_login_exitoso(http_client, cliente_normal):
    response = await http_client.post("/api/v1/login", json={
        "correo": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_login_fallido(http_client, cliente_normal):
    response = await http_client.post("/api/v1/login", json={
        "correo": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Correo o contraseña incorrectos"

@pytest.mark.asyncio
async def test_login_bloqueado(http_client, cliente_bloqueado):
    response = await http_client.post("/api/v1/login", json={
        "correo": "bloqueado@example.com",
        "password": "password123"
    })
    assert response.status_code == 429
    assert "bloqueada" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_usuario_no_existe(http_client):
    response = await http_client.post("/api/v1/login", json={
        "correo": "noexiste@example.com",
        "password": "password123"
    })
    assert response.status_code == 401