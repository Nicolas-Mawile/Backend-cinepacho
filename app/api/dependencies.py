"""API dependencies for authentication and authorization."""

from fastapi import Depends
from fastapi import HTTPException

from fastapi.security import OAuth2PasswordBearer

from jose import jwt
from jose import JWTError

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from typing import List

from app.config import settings

from app.database import get_db

from app.infrastructure.models.usuario import (
    Usuario
)

from app.infrastructure.models.rol import Rol
from app.infrastructure.models.token_revocado import TokenRevocado


# =========================================================
# OAUTH
# =========================================================

oauth2Scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

# importante:
# auto_error=False
# para soportar invitados

oauth2OptionalScheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)


# =========================================================
# USER AUTH
# =========================================================

def get_current_user(
    token: str = Depends(oauth2Scheme),
    db: Session = Depends(get_db)
):
    """
    Decodifica JWT y devuelve
    usuario autenticado.
    """

    invalidTokenException = HTTPException(
        status_code=401,
        detail="Token inválido"
    )

    try:

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        userId = payload.get("sub")

        if userId is None:

            raise invalidTokenException

        jti = payload.get("jti")
        if jti and db.query(TokenRevocado).filter(TokenRevocado.jti == jti).first():
            raise invalidTokenException

    except JWTError:

        raise invalidTokenException

    usuario = (
        db.query(Usuario)
        .options(
            joinedload(Usuario.rol)
            .joinedload(Rol.permisos),

            joinedload(Usuario.cliente),

            joinedload(Usuario.empleado)
        )
        .filter(
            Usuario.id == int(userId)
        )
        .first()
    )

    if usuario is None:

        raise invalidTokenException

    return usuario


# =========================================================
# USER OPTIONAL
# =========================================================

def getCurrentUserOptional(
    token: str | None = Depends(
        oauth2OptionalScheme
    ),
    db: Session = Depends(get_db)
):
    """
    Retorna usuario autenticado
    o None si no hay token.
    """

    if not token:

        return None

    try:

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        userId = payload.get("sub")

        if userId is None:

            return None

        jti = payload.get("jti")
        if jti and db.query(TokenRevocado).filter(TokenRevocado.jti == jti).first():
            return None

    except JWTError:

        return None

    usuario = (
        db.query(Usuario)
        .options(
            joinedload(Usuario.rol)
            .joinedload(Rol.permisos),

            joinedload(Usuario.cliente),

            joinedload(Usuario.empleado)
        )
        .filter(
            Usuario.id == int(userId)
        )
        .first()
    )

    return usuario


# =========================================================
# ROLE VALIDATION
# =========================================================

def requireRole(
    roles: List[str]
):
    """
    Restringe acceso por rol.
    """

    def validator(
        user: Usuario = Depends(
            get_current_user
        )
    ):

        if user.rol is None:

            raise HTTPException(
                status_code=403,
                detail="Usuario sin rol asignado"
            )

        if user.rol.nombre not in roles:

            raise HTTPException(
                status_code=403,
                detail="No autorizado"
            )

        return user

    return validator


# =========================================================
# PERMISSION VALIDATION
# =========================================================

def requirePermission(
    permission: str
):
    """
    Restringe acceso por permisos.
    """

    def validator(
        user: Usuario = Depends(
            get_current_user
        )
    ):

        if user.rol is None:

            raise HTTPException(
                status_code=403,
                detail="Usuario sin rol"
            )

        permisos = [
            permiso.nombre
            for permiso in user.rol.permisos
        ]

        if permission not in permisos:

            raise HTTPException(
                status_code=403,
                detail="Permiso insuficiente"
            )

        return user

    return validator


# =========================================================
# MULTIPLEX ACCESS
# =========================================================

def validateMultiplexAccess(
    user: Usuario,
    multiplexId: int
):
    """
    Valida acceso por multiplex.
    """

    if (
        user.rol.nombre
        == "ADMIN-GENERAL"
    ):

        return

    empleado = user.empleado

    if empleado is None:

        raise HTTPException(
            status_code=403,
            detail=(
                "Usuario no asociado "
                "a empleado"
            )
        )

    contrato = empleado.contratoActivo

    if contrato is None:

        raise HTTPException(
            status_code=403,
            detail=(
                "Empleado sin "
                "contrato activo"
            )
        )

    if contrato.multiplexId != multiplexId:

        raise HTTPException(
            status_code=403,
            detail="No autorizado para este multiplex",
        )
