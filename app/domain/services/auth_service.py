"""Auth domain service."""
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.config import settings
from app.infrastructure.repositories.cliente_repository import ClienteRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def crear_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

async def authenticate_user(correo: str, password: str, repo: ClienteRepository):
    cliente = await repo.get_by_correo(correo)

    if not cliente:
        return None, "credenciales_invalidas"

    if await repo.esta_bloqueado(cliente):
        tiempo_restante = 15 - int(
            (datetime.utcnow() - cliente.ultimo_intento).seconds / 60
        )
        return None, f"bloqueado:{tiempo_restante}"

    if not pwd_context.verify(password, cliente.password_hash):
        await repo.incrementar_intentos(cliente)
        if cliente.intentos_fallidos >= 5:
            return None, f"bloqueado:15"
        return None, "credenciales_invalidas"

    await repo.reset_intentos(cliente)

    access_token = crear_token(
        {"sub": str(cliente.id), "tipo": "access"},
        timedelta(hours=24)
    )
    refresh_token = crear_token(
        {"sub": str(cliente.id), "tipo": "refresh"},
        timedelta(days=7)
    )

    return {"access_token": access_token, "refresh_token": refresh_token}, None