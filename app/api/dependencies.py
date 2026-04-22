"""API dependencies for authentication and authorization."""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.models.cliente import Cliente
from app.models.empleado import Empleado
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        subject: str = payload.get("sub")
        tipo: str = payload.get("tipo")
        if subject is None or tipo != "access":
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # Buscar en clientes o empleados según el tipo de usuario
    kind: str = payload.get("kind", "cliente")
    if kind == "cliente":
        result = await db.execute(select(Cliente).where(Cliente.id == int(subject)))
        user = result.scalar_one_or_none()
    else:
        result = await db.execute(select(Empleado).where(Empleado.id == int(subject)))
        user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user

async def get_current_cliente(user=Depends(get_current_user)):
    if not isinstance(user, Cliente):
        raise HTTPException(status_code=403, detail="Se requiere rol de cliente")
    return user

async def get_current_cajero(user=Depends(get_current_user)):
    if not isinstance(user, Empleado) or user.cargo != "cajero":
        raise HTTPException(status_code=403, detail="Se requiere rol de cajero")
    return user

async def get_current_admin_mx(user=Depends(get_current_user)):
    if not isinstance(user, Empleado) or user.cargo != "admin_multiplex":
        raise HTTPException(status_code=403, detail="Se requiere rol de admin_multiplex")
    return user

async def get_current_admin_general(user=Depends(get_current_user)):
    if not isinstance(user, Empleado) or user.cargo != "admin_general":
        raise HTTPException(status_code=403, detail="Se requiere rol de admin_general")
    return user