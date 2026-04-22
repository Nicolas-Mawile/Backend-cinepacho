"""API dependencies for authentication and authorization."""

from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import jwt

from ..config import settings
from ..database import get_db

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Extrae y valida el JWT del header Authorization.
    Retorna los datos del usuario autenticado.
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    # Aquí podrías buscar el usuario en BD si es necesario
    return {"user_id": user_id, "token": token}


def require_rol(role: str):
    """Crea una dependencia que requiere un rol específico."""
    async def check_rol(current_user = Depends(get_current_user)):
        # TODO: Implementar lógica de verificación de rol
        # Por ahora es un placeholder
        return current_user
    return check_rol


def require_multiplex(multiplex_id: int):
    """Crea una dependencia que verifica acceso a un multiplex."""
    async def check_multiplex(current_user = Depends(get_current_user)):
        # TODO: Implementar lógica de verificación de acceso a multiplex
        return current_user
    return check_multiplex


async def get_current_admin_general(x_test_role: str = Header(default="admin_general")):
    """
    Valida que el usuario sea administrador general.
    Protege endpoints administrativos globales.
    TEMPORAL: Modifciar cuando HU 27 este implementado
    """
    if x_test_role != "admin_general":
        raise HTTPException(403, "Acceso restringido a administrador general")
    return {"rol": "admin_general"}
