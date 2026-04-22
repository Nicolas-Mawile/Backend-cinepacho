"""Auth endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.cliente_repository import ClienteRepository
from app.domain.services.auth_service import authenticate_user
from app.api.dependencies import get_current_user
from app.database import get_db

router = APIRouter()

class LoginRequest(BaseModel):
    correo: str
    password: str

@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    tokens, error = await authenticate_user(data.correo, data.password,
                                            ClienteRepository(db))
    if error == "credenciales_invalidas":
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    if error and error.startswith("bloqueado"):
        minutos = error.split(":")[1]
        raise HTTPException(status_code=429,
                            detail=f"Cuenta bloqueada. Intenta en {minutos} minutos")
    return tokens

@router.post("/registro")
async def registro():
    raise HTTPException(status_code=501, detail="No implementado")

@router.post("/refresh")
async def refresh():
    return {"message": "refresh"}

@router.get("/me")
async def me(user=Depends(get_current_user)):
    return {"id": user.id, "correo": user.correo}