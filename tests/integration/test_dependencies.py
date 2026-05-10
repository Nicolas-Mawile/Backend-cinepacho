"""Integration tests for dependencies."""
import pytest
from app.domain.services.auth_service import crear_token
from datetime import timedelta

@pytest.mark.asyncio
async def test_token_invalido_retorna_401(http_client):
    response = await http_client.get(
        "/api/v1/me",
        headers={"Authorization": "Bearer token_invalido"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_sin_token_retorna_401(http_client):
    response = await http_client.get("/api/v1/me")
    assert response.status_code == 401