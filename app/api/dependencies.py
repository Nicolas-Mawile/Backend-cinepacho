"""API dependencies for authentication and authorization."""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from app.config import settings
from app.models.cliente import Cliente
from app.models.empleado import Empleado
from app.database import get_db
from app.domain.roles import get_permisos

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        subject: str = payload.get("sub")
        tipo: str = payload.get("tipo")
        if subject is None or tipo != "access":
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    kind: str = payload.get("kind", "cliente")
    if kind == "cliente":
        result = db.execute(select(Cliente).where(Cliente.id == int(subject)))
        user = result.scalar_one_or_none()
    else:
        result = db.execute(select(Empleado).where(Empleado.id == int(subject)))
        user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user

async def get_current_cliente(user=Depends(get_current_user)):
    if not isinstance(user, Cliente):
        raise HTTPException(status_code=403, detail="Se requiere rol CLIENTE")
    return user

async def get_current_cajero(user=Depends(get_current_user)):
    if not isinstance(user, Empleado) or user.rol != "EMPLEADO-CAJERO":
        raise HTTPException(status_code=403, detail="Se requiere rol EMPLEADO-CAJERO")
    return user

async def get_current_admin_mx(user=Depends(get_current_user)):
    if not isinstance(user, Empleado) or user.rol != "ADMIN-MULTIPLEX":
        raise HTTPException(status_code=403, detail="Se requiere rol ADMIN-MULTIPLEX")
    return user

async def get_current_admin_general(user=Depends(get_current_user)):
    if not isinstance(user, Empleado) or user.rol != "ADMIN-GENERAL":
        raise HTTPException(status_code=403, detail="Se requiere rol ADMIN-GENERAL")
    return user

def require_rol(role: str):
    def check_rol(current_user=Depends(get_current_user)):
        return current_user
    return check_rol

def require_role(roles_permitidos: List[str]):
    async def checker(user=Depends(get_current_user)):
        rol = "CLIENTE" if isinstance(user, Cliente) else user.rol
        if rol not in roles_permitidos and "ADMIN-GENERAL" not in roles_permitidos:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        return user
    return checker

def require_permiso(permiso: str):
    async def checker(user=Depends(get_current_user)):
        rol = "CLIENTE" if isinstance(user, Cliente) else user.rol
        if permiso not in get_permisos(rol):
            raise HTTPException(status_code=403, detail=f"Permiso requerido: {permiso}")
        return user
    return checker

def require_multiplex(multiplex_id: int):
    def check_multiplex(current_user=Depends(get_current_user)):
        return current_user
    return check_multiplex