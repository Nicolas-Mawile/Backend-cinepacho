"""Auth domain service."""

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.config import settings
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.repositories.cliente_repository import ClienteRepository
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository


class AuthService:
    """Servicio de dominio para autenticación y gestión de tokens."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Genera un hash bcrypt de la contraseña."""
        # bcrypt requiere bytes y maneja el truncamiento a 72 bytes automáticamente o lanza error.
        # Aquí lo hacemos explícito para evitar problemas.
        pwd_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash."""
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        """Genera un JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    def registrar_cliente(self, repo: ClienteRepository, nombre: str, correo: str, password: str) -> Cliente:
        """
        Registra un nuevo cliente en el sistema.
        
        Args:
            repo: Repositorio de clientes
            nombre: Nombre completo
            correo: Correo electrónico (debe ser único)
            password: Contraseña en texto plano
            
        Returns:
            El cliente creado
        """
        # El repositorio ya tiene existe_correo(), pero la lógica de negocio 
        # de "no permitir duplicados" vive aquí o se valida en el endpoint.
        # Aquí procedemos a crear la entidad.
        
        hashed_pw = self.hash_password(password)
        
        nuevo_cliente = Cliente(
            nombre_completo=nombre,
            correo=correo,
            password_hash=hashed_pw
        )
        
        return repo.add(nuevo_cliente)


# Funciones de compatibilidad para código existente
def crear_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def authenticate_user(correo: str, password: str, repo: ClienteRepository, rt_repo=None):
    from app.domain.roles import get_permisos
    cliente = repo.buscar_por_correo(correo)
    if not cliente:
        return None, "credenciales_invalidas"

    if repo.verificar_bloqueo(correo):
        ultimo_intento = cliente.ultimo_intento
        if ultimo_intento and ultimo_intento.tzinfo is None:
            ultimo_intento = ultimo_intento.replace(tzinfo=timezone.utc)
        tiempo_restante = 15 - int((datetime.now(timezone.utc) - ultimo_intento).seconds / 60)
        return None, f"bloqueado:{tiempo_restante}"

    auth_service = AuthService()
    if not auth_service.verify_password(correo, cliente.password_hash):
        repo.registrar_intento_fallido(correo)
        cliente_actualizado = repo.buscar_por_correo(correo)
        if cliente_actualizado.intentos_fallidos >= 5:
            return None, "bloqueado:15"
        return None, "credenciales_invalidas"

    repo.reset_intentos(correo)
    refresh_expires = timedelta(days=7)

    access_token = crear_token(
        {"sub": str(cliente.id), "tipo": "access", "kind": "cliente",
         "rol": "CLIENTE", "permisos": get_permisos("CLIENTE")},
        timedelta(hours=24)
    )
    refresh_token = crear_token(
        {"sub": str(cliente.id), "tipo": "refresh", "kind": "cliente"},
        refresh_expires
    )

    if rt_repo:
        rt_repo.guardar(cliente_id=cliente.id, token=refresh_token,
                        expires_at=datetime.now(timezone.utc) + refresh_expires)

    return {"access_token": access_token, "refresh_token": refresh_token,
            "rol": "CLIENTE", "permisos": get_permisos("CLIENTE")}, None


def authenticate_empleado(correo: str, password: str, db):
    from sqlalchemy import select
    from app.infrastructure.models.empleado import Empleado
    from app.domain.roles import get_permisos

    result = db.execute(select(Empleado).where(Empleado.correo == correo))
    empleado = result.scalar_one_or_none()

    if not empleado or not empleado.activo:
        return None, "credenciales_invalidas"
    
    auth_service = AuthService()
    if not auth_service.verify_password(correo, empleado.password_hash):
        return None, "credenciales_invalidas"

    refresh_expires = timedelta(days=7)
    access_token = crear_token(
        {"sub": str(empleado.id), "tipo": "access", "kind": "empleado",
         "rol": empleado.rol, "permisos": get_permisos(empleado.rol)},
        timedelta(hours=24)
    )
    refresh_token = crear_token(
        {"sub": str(empleado.id), "tipo": "refresh", "kind": "empleado"},
        refresh_expires
    )

    return {"access_token": access_token, "refresh_token": refresh_token,
            "rol": empleado.rol, "permisos": get_permisos(empleado.rol)}, None
