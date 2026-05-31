from datetime import datetime, timezone, timedelta
from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.database import get_db
from app.api.schemas.auth import AuthResponse, RegistroRequest, LoginRequest, SolicitarResetRequest, ResetPasswordRequest
from app.domain.services.email_service import EmailService
from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.rol import Rol
from app.infrastructure.repositories.usuarioRepository import UsuarioRepository
from app.domain.services.auth_service import AuthService
from app.api.dependencies import get_current_user, oauth2Scheme
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.models.token_revocado import TokenRevocado
from app.utils.timezone import nowNaive, nowColombia
from app.infrastructure.models.recompensaBoleta import RecompensaBoleta
from app.infrastructure.models.tipoSilla import TipoSilla
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


def _precios_sillas(db) -> dict:
    """Devuelve los precios de boleta general y preferencial desde la BD."""
    tipos = db.query(TipoSilla).all()
    precios = {"precioBoletaGeneral": None, "precioBoletaPreferencial": None}
    for t in tipos:
        nombre = t.nombre.lower()
        if nombre == "general":
            precios["precioBoletaGeneral"] = t.precio
        elif nombre == "preferencial":
            precios["precioBoletaPreferencial"] = t.precio
    return precios

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
    
    if usuario.bloqueadoHasta and usuario.bloqueadoHasta > nowNaive():
        raise HTTPException(status_code=403, detail="Usuario bloqueado temporalmente")

    validPassword = authService.verifyPassword(data.password, usuario.passwordHash)
    if not validPassword:
        usuario.intentosFallidos += 1

        if usuario.intentosFallidos >= 5:
            usuario.bloqueadoHasta = nowNaive() + timedelta(minutes=15)
        
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

    contrato = usuario.empleado.contratoActivo if usuario.empleado else None
    recompensasDisponibles = 0

    if usuario.cliente:

        recompensasDisponibles = (
            db.query(RecompensaBoleta)
            .filter(
                RecompensaBoleta.clienteId == usuario.cliente.id,
                RecompensaBoleta.utilizada == False,
                RecompensaBoleta.fechaVencimiento > nowNaive(),).count())

    precios = _precios_sillas(db)

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
            "empleado_id": usuario.empleado.id if usuario.empleado else None,
            "multiplexId": contrato.multiplexId if contrato else None,
            "puntosAcumulados": (usuario.cliente.puntosAcumulados if usuario.cliente else None),
            "recompensasDisponibles": (recompensasDisponibles if usuario.cliente else 0),
            "precioBoletaGeneral": precios["precioBoletaGeneral"],
            "precioBoletaPreferencial": precios["precioBoletaPreferencial"],
        }
    }

@router.post("/logout")
def logout(token: str = Depends(oauth2Scheme), db: Session = Depends(get_db)):
    """Invalida el token JWT actual registrándolo en la lista negra."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti:
            raise HTTPException(status_code=400, detail="Token sin identificador único")

        ya_revocado = db.query(TokenRevocado).filter(TokenRevocado.jti == jti).first()
        if not ya_revocado:
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc).replace(tzinfo=None)
            db.add(TokenRevocado(jti=jti, expiresAt=expires_at))
            db.commit()

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    return {"message": "Sesión cerrada correctamente"}


@router.get("/me")
def me(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Devuelve los datos del usuario autenticado."""
    permisos = [permiso.nombre for permiso in user.rol.permisos]
    if user.cliente:
        correo = user.cliente.correo
    else:
        correo = user.empleado.correoLaboral

    contrato = user.empleado.contratoActivo if user.empleado else None
    precios = _precios_sillas(db)
    return {
        "id": user.id,
        "nombres": user.nombres,
        "apellidos": user.apellidos,
        "correo": correo,
        "rol": user.rol.nombre,
        "permisos": permisos,
        "empleado_id": user.empleado.id if user.empleado else None,
        "multiplexId": contrato.multiplexId if contrato else None,
        "puntosAcumulados": user.cliente.puntosAcumulados if user.cliente else None,
        "precioBoletaGeneral": precios["precioBoletaGeneral"],
        "precioBoletaPreferencial": precios["precioBoletaPreferencial"],
    }

@router.post("/solicitar-reset")
def solicitar_reset(datos: SolicitarResetRequest, db: Session = Depends(get_db)):
    """Genera un token de reset y envía el link por correo."""
    usuario = UsuarioRepository(db).buscarPorCorreo(datos.correo)

    # Siempre devuelve 200 para no revelar si el correo existe
    if not usuario:
        return {"mensaje": "Si el correo existe, recibirás un enlace de recuperación"}

    token = jwt.encode(
        {
            "userId": usuario.id,
            "type": "password-reset",
            "exp": nowColombia() + timedelta(minutes=15),
        },
        settings.secret_key,
        algorithm="HS256",
    )

    link_reset = f"{settings.frontend_url}/restablecer-contrasena?token={token}"

    print("\n========== LINK RESET CONTRASEÑA ==========")
    print(link_reset)
    print("===========================================\n")

    EmailService().enviar_reset_password(
        destinatario=usuario.correo,
        link_reset=link_reset,
    )

    return {"mensaje": "Si el correo existe, recibirás un enlace de recuperación"}


@router.post("/reset-password")
def reset_password(datos: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Valida el token de reset y actualiza la contraseña del usuario."""
    try:
        payload = jwt.decode(datos.token, settings.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El enlace de recuperación expiró")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido")

    if payload.get("type") != "password-reset":
        raise HTTPException(status_code=400, detail="Token inválido")

    user_id = payload.get("userId")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token inválido")

    usuario = UsuarioRepository(db).buscarPorId(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    authService = AuthService()
    usuario.passwordHash = authService.hashPassword(datos.nueva_password)
    usuario.intentosFallidos = 0
    usuario.bloqueadoHasta = None
    db.commit()

    return {"mensaje": "Contraseña actualizada correctamente"}


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
