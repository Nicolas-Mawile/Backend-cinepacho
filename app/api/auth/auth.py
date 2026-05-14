from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.schemas.auth import RegistroRequest, LoginRequest
from app.infrastructure.models.persona import Persona
from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.rol import Rol
from app.infrastructure.repositories.usuarioRepository import UsuarioRepository
from app.domain.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.repositories.cliente_repository import ClienteRepository

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

def _buildUsuarioResponse(usuario: Usuario) -> dict:
    """Construye la respuesta JSON para un usuario autenticado."""
    permisos = [permiso.nombre for permiso in usuario.rol.permisos]
    return {
        "id": usuario.id,
        "nombres": usuario.persona.nombres,
        "apellidos": usuario.persona.apellidos,
        "correo": usuario.persona.correo,
        "rol": usuario.rol.nombre,
        "permisos": permisos
    }

@router.post("/registro")
def registro(datos: RegistroRequest, db: Session = Depends(get_db)):
    """Registra un nuevo usuario y genera un token de acceso. ES PARA REGISTRAR CLIENTES, LOS EMPLEADOS LOS REGISTRAN LOS ADMIN."""
    usuarioRepo = UsuarioRepository(db)
    authService = AuthService()

    existeUsuario = usuarioRepo.buscarPorCorreo(datos.correo)
    if existeUsuario:
        raise HTTPException(status_code=409, detail="Correo ya registrado")


    rolCliente = db.query(Rol).filter(Rol.nombre == "CLIENTE").first()
    if not rolCliente:
        raise HTTPException(status_code=500, detail="Rol CLIENTE no existe")
    
    cliente = Cliente(
        nombres = datos.nombres,
        apellidos = datos.apellidos,
        correo = datos.correo,
        telefono = datos.telefono
    )
    db.add(cliente)
    db.flush()

    usuario = Usuario(
        passwordHash=authService.hashPassword(datos.password),
        personaId=cliente.id,
        rolId=rolCliente.id)

    db.add(usuario)
    db.flush()

    cliente.usuarioId = usuario.id
    db.commit()

    db.refresh(cliente)
    db.refresh(usuario)

    
    token = authService.createAccessToken(data={"sub": str(usuario.id), "role": usuario.rol.nombre})
    refreshToken = (authService.createRefreshToken(data={"sub": str(usuario.id)}))
    return {"access_token": token,
            "token_type": "bearer",
            "refresh_token": refreshToken,
            "usuario": _buildUsuarioResponse(usuario)}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Valida credenciales y devuelve un token JWT de acceso."""
    usuarioRepo = UsuarioRepository(db)
    authService = AuthService()

    usuario = usuarioRepo.buscarPorCorreo(data.correo)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    if not usuario.estaActivo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    
    if usuario.bloqueadoHasta and usuario.bloqueadoHasta > datetime.now(datetime.timezone.utc):
        raise HTTPException(status_code=403, detail="Usuario bloqueado temporalmente")

    validPassword = authService.verifyPassword(data.password, usuario.passwordHash)
    if not validPassword:
        usuario.intentosFallidos += 1

        if usuario.intentosFallidos >= 5:
            from datetime import timedelta
            usuario.bloqueadoHasta = datetime.now(datetime.timezone.utc) + timedelta(minutes=15)
        
        db.commit()
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    usuario.intentosFallidos = 0
    usuario.bloqueadoHasta = None
    db.commit()

    accessToken = authService.createAccessToken(data={"sub": str(usuario.id), "role": usuario.rol.nombre})
    refreshToken = authService.createRefreshToken(data={"sub": str(usuario.id)})
    
    return {
        "access_token": accessToken,
        "token_type": "bearer",
        "refresh_token": refreshToken,
        "usuario": _buildUsuarioResponse(usuario)
    }

@router.get("/me")
def me(user=Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado."""
    permisos = [permiso.nombre for permiso in user.rol.permisos]
    return {
        "id": user.id,
        "nombres": user.persona.nombres,
        "apellidos": user.persona.apellidos,
        "correo": user.persona.correo,
        "rol": user.rol.nombre,
        "permisos": permisos
    }