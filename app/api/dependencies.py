"""API dependencies for authentication and authorization."""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.config import settings
from app.database import get_db
from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.rol import Rol

oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

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

    usuario = (db.query(Usuario).options(joinedload(Usuario.rol).joinedload(Rol.permisos), joinedload(Usuario.cliente), joinedload(Usuario.empleado))
               .filter(Usuario.id == int(userId)).first())
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
    
    contrato = empleado.contratoActivo
    if contrato is None:
        raise HTTPException(status_code=403, detail="Empleado sin contrato activo")

    if empleado.multiplexId != multiplexId:
        raise HTTPException(status_code=403, detail="No autorizado para este multiplex")
