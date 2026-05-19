from datetime import datetime, timezone, timedelta
from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.schemas.auth import AuthResponse, RegistroRequest, LoginRequest
from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.rol import Rol
from app.infrastructure.repositories.usuarioRepository import UsuarioRepository
from app.domain.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.infrastructure.models.cliente import Cliente

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/registro")
def registro(datos: RegistroRequest, db: Session = Depends(get_db)):
    """Registra un nuevo usuario y genera un token de acceso. 
        ES PARA REGISTRAR CLIENTES, LOS EMPLEADOS LOS REGISTRAN LOS ADMIN."""
    usuarioRepo = UsuarioRepository(db)
    authService = AuthService()

    existeUsuario = usuarioRepo.buscarPorCorreo(datos.correo)
    if existeUsuario:
        raise HTTPException(status_code=409, detail="Correo ya registrado")
    
    cliente = Cliente(nombres = datos.nombres, apellidos = datos.apellidos, 
                      correo = datos.correo, telefono = datos.telefono)
    db.add(cliente)
    db.flush()

    stmtRolCliente = select(Rol).where(Rol.nombre == "CLIENTE")
    rolCliente = db.execute(stmtRolCliente).scalars().first()
    if not rolCliente:
        raise HTTPException(status_code=500, detail="Rol CLIENTE no existe")

    usuario = Usuario(
        clienteId=cliente.id,
        passwordHash=authService.hashPassword(datos.password),
        rolId=rolCliente.id)

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    
    token = authService.createAccessToken(data={"sub": str(usuario.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "correo": cliente.correo,
            "nombres": cliente.nombres,
            "apellidos": cliente.apellidos,
            "rol": usuario.rol.nombre,
            "permisos": [permiso.nombre for permiso in usuario.rol.permisos]
        }
    }


@router.post("/login", response_model=AuthResponse)
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
            usuario.bloqueadoHasta = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        db.commit()
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    usuario.intentosFallidos = 0
    usuario.bloqueadoHasta = None
    db.commit()

    accessToken = authService.createAccessToken(data={"sub": str(usuario.id)})
    if usuario.cliente:
        correo = usuario.cliente.correo
    else:
        correo = usuario.empleado.correoLaboral

    return {
        "access_token": accessToken,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "correo": correo,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "rol": usuario.rol.nombre,
            "permisos": [permiso.nombre for permiso in usuario.rol.permisos],
            "empleado_id": usuario.empleado.id if usuario.empleado else None
        }
    }

@router.get("/me")
def me(user=Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado."""
    permisos = [permiso.nombre for permiso in user.rol.permisos]
    if user.cliente:
        correo = user.cliente.correo
    else:        
        correo = user.empleado.correoLaboral
    return {
        "id": user.id,
        "nombres": user.nombres,
        "apellidos": user.apellidos,
        "correo": correo,
        "rol": user.rol.nombre,
        "permisos": permisos
    }

# def _buildUsuarioResponse(usuario: Usuario) -> dict:
#     """Construye la respuesta JSON para un usuario autenticado."""
#     permisos = [permiso.nombre for permiso in usuario.rol.permisos]
#     return {
#         "id": usuario.id,
#         "nombres": usuario.persona.nombres,
#         "apellidos": usuario.persona.apellidos,
#         "correo": usuario.persona.correo,
#         "rol": usuario.rol.nombre,
#         "permisos": permisos
#     }