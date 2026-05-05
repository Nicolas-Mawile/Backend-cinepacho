"""Auth domain service."""

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.config import settings
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.repositories.cliente_repository import ClienteRepository

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
