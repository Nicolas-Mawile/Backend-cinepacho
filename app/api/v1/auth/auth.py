"""Authentication endpoints."""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.auth import RegistroRequest, AuthResponse
from app.infrastructure.repositories.cliente_repository import ClienteRepository
from app.domain.services.auth_service import AuthService
from app.infrastructure.email import enviar_bienvenida
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_cliente_repository(db: Session = Depends(get_db)):
    return ClienteRepository(db)

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
