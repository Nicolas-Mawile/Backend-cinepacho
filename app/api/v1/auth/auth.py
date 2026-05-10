"""Authentication endpoints - Consolidated."""
import asyncio
from datetime import timedelta
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.api.schemas.auth import RegistroRequest, AuthResponse
from app.infrastructure.repositories.cliente_repository import ClienteRepository
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.services.auth_service import AuthService, authenticate_user, authenticate_empleado, crear_token
from app.infrastructure.email import enviar_bienvenida
from app.database import get_db
from app.config import settings
from app.api.dependencies import get_current_user
from app.domain.roles import get_permisos
from app.infrastructure.models.cliente import Cliente

router = APIRouter(prefix="/auth", tags=["Auth"])

# ==================== Request/Response Models ====================
class LoginRequest(BaseModel):
    correo: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

# ==================== Helpers ====================
def get_cliente_repository(db: Session = Depends(get_db)):
    return ClienteRepository(db)

# ==================== Endpoints ====================

@router.post("/registro", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def registro(
    datos: RegistroRequest,
    repo: ClienteRepository = Depends(get_cliente_repository),
    auth_service: AuthService = Depends()
):
    """
    Registra un nuevo cliente y retorna un token de acceso.
    """
    # 1. Verificar si el correo ya existe
    if repo.existe_correo(datos.correo):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado"
        )
    
    # 2. Registrar cliente (hasheo ocurre en el servicio)
    nuevo_cliente = auth_service.registrar_cliente(
        repo=repo,
        nombre=datos.nombre,
        correo=datos.correo,
        password=datos.password
    )
    
    # 3. Generar token
    access_token = auth_service.create_access_token(
        data={"sub": str(nuevo_cliente.id), "email": nuevo_cliente.correo}
    )
    
    # 4. Enviar correo de bienvenida (asíncrono)
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(
            asyncio.to_thread(enviar_bienvenida, nuevo_cliente.nombre_completo, nuevo_cliente.correo)
        )
    except RuntimeError:
        # Si no hay loop corriendo (e.g. en algunos contextos de test sincrónicos), 
        # ignoramos el envío de correo para no romper la respuesta.
        pass
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "cliente": nuevo_cliente
    }


@router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Inicia sesión de un cliente existente.
    Retorna access_token y refresh_token.
    """
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
    """
    Renueva el access token usando un refresh token válido.
    """
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
    """
    Inicia sesión de un empleado.
    Retorna access_token y refresh_token con rol de empleado.
    """
    tokens, error = authenticate_empleado(data.correo, data.password, db)
    if error:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return tokens


@router.get("/me")
async def me(user=Depends(get_current_user)):
    """
    Obtiene los datos del usuario autenticado actualmente.
    """
    rol = "CLIENTE" if isinstance(user, Cliente) else user.rol
    return {
        "id": user.id,
        "correo": user.correo,
        "nombre": user.nombre,
        "rol": rol,
        "permisos": get_permisos(rol)
    }
