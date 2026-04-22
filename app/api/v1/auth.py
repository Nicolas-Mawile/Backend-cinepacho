"""Auth endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from app.infrastructure.repositories.cliente_repository import ClienteRepository
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.services.auth_service import authenticate_user, crear_token
from app.api.dependencies import get_current_user
from app.database import get_db
from app.config import settings
from datetime import timedelta

router = APIRouter()

class LoginRequest(BaseModel):
    correo: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    tokens, error = await authenticate_user(
        data.correo, data.password,
        ClienteRepository(db),
        RefreshTokenRepository(db)
    )
    if error == "credenciales_invalidas":
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    if error and error.startswith("bloqueado"):
        minutos = error.split(":")[1]
        raise HTTPException(status_code=429, detail=f"Cuenta bloqueada. Intenta en {minutos} minutos")
    return tokens

@router.post("/refresh")
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    rt_repo = RefreshTokenRepository(db)

    # Verificar firma JWT
    try:
        payload = jwt.decode(data.refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("tipo") != "refresh":
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # Verificar que no esté revocado
    rt = await rt_repo.buscar_valido(data.refresh_token)
    if rt is None:
        raise HTTPException(status_code=401, detail="Refresh token inválido o ya utilizado")

    # Revocar (one-time use)
    await rt_repo.revocar(data.refresh_token)

    # Generar nuevo access token
    cliente_id = payload.get("sub")
    access_token = crear_token(
        {"sub": cliente_id, "tipo": "access", "kind": payload.get("kind", "cliente")},
        timedelta(hours=24)
    )
    return {"access_token": access_token}

@router.post("/registro")
async def registro():
    raise HTTPException(status_code=501, detail="No implementado")

@router.get("/me")
async def me(user=Depends(get_current_user)):
    return {"id": user.id, "correo": user.correo}