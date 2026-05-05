"""Auth endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.domain.roles import get_permisos
from app.infrastructure.repositories.cliente_repository import ClienteRepository
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.services.auth_service import authenticate_user, authenticate_empleado, crear_token
from app.api.dependencies import get_current_user
from app.database import get_db
from app.config import settings
from datetime import timedelta
from app.models.cliente import Cliente

router = APIRouter()

class LoginRequest(BaseModel):
    correo: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    tokens, error = authenticate_user(
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
async def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    rt_repo = RefreshTokenRepository(db)
    try:
        payload = jwt.decode(data.refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("tipo") != "refresh":
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    rt = rt_repo.buscar_valido(data.refresh_token)
    if rt is None:
        raise HTTPException(status_code=401, detail="Refresh token inválido o ya utilizado")

    rt_repo.revocar(data.refresh_token)

    cliente_id = payload.get("sub")
    access_token = crear_token(
        {"sub": cliente_id, "tipo": "access", "kind": payload.get("kind", "cliente")},
        timedelta(hours=24)
    )
    return {"access_token": access_token}

@router.post("/login/empleado")
async def login_empleado(data: LoginRequest, db: Session = Depends(get_db)):
    tokens, error = authenticate_empleado(data.correo, data.password, db)
    if error:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return tokens

@router.post("/registro")
async def registro():
    raise HTTPException(status_code=501, detail="No implementado")

@router.get("/me")
async def me(user=Depends(get_current_user)):
    rol = "CLIENTE" if isinstance(user, Cliente) else user.rol
    return {
        "id": user.id,
        "correo": user.correo,
        "nombre": user.nombre,
        "rol": rol,
        "permisos": get_permisos(rol)
    }