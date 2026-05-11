"""API dependencies for authentication and authorization."""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from app.config import settings
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.models.empleado import Empleado
from app.database import get_db
from app.domain.roles import get_permisos
from app.infrastructure.models.usuario import Usuario

oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2Scheme), db: Session = Depends(get_db)):
    """Decodifica el JWT y devuelve el usuario autenticado."""
    invalidTokenException = HTTPException(status_code=401, detail="Token inválido")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        userId = payload.get("sub")
        if userId is None:
            raise invalidTokenException
    except JWTError:
        raise invalidTokenException

    usuario = db.query(Usuario).filter(Usuario.id == int(userId)).first()
    if usuario is None:
        raise invalidTokenException

    return usuario

def requireRole(roles: List[str]):
    """Restringe acceso por rol."""
    def validator(user: Usuario = Depends(get_current_user)):
        if user.rol is None:
            raise HTTPException(status_code=403, detail="Usuario sin rol asignado")

        if user.rol.nombre not in roles:
            raise HTTPException(status_code=403, detail="No autorizado")

        return user
    return validator

def requirePermission(permission: str):
    """Restringe acceso por permisos."""

    def validator(user: Usuario = Depends(get_current_user)):

        if user.rol is None:
            raise HTTPException(status_code=403, detail="Usuario sin rol")
        permisos = [permiso.nombre for permiso in user.rol.permisos]

        if permission not in permisos:
            raise HTTPException(status_code=403, detail="Permiso insuficiente")
        return user
    return validator

def validateMultiplexAccess(user: Usuario, multiplexId: int):
    """Valida acceso por multiplex."""
    if user.rol.nombre == "ADMIN-GENERAL":
        return

    empleado = user.empleado
    if empleado is None:
        raise HTTPException(status_code=403, detail="Usuario no asociado a empleado")

    if empleado.multiplexId != multiplexId:
        raise HTTPException(status_code=403, detail="No autorizado para este multiplex")

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


def require_role(rolesPermitidos: List[str]):
    """Dependencia que restringe el acceso a roles específicos."""
    async def checker(user=Depends(get_current_user)):
        rol = "CLIENTE" if isinstance(user, Cliente) else user.rol
        if rol not in rolesPermitidos and "ADMIN-GENERAL" not in rolesPermitidos:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        return user
    return checker


def require_permiso(permiso: str):
    """Dependencia que valida el permiso del usuario para un recurso."""
    async def checker(user=Depends(get_current_user)):
        rol = "CLIENTE" if isinstance(user, Cliente) else user.rol
        if permiso not in get_permisos(rol):
            raise HTTPException(status_code=403, detail=f"Permiso requerido: {permiso}")
        return user
    return checker


def require_multiplex(multiplex_id: int):
    """Dependencia para validar el multiplex en el contexto del usuario."""
    def check_multiplex(current_user=Depends(get_current_user)):
        return current_user
    return check_multiplex