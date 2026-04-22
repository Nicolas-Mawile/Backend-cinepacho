"""Auth domain service."""
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.config import settings
from app.infrastructure.repositories.cliente_repository import ClienteRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def crear_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

async def authenticate_user(correo: str, password: str, repo: ClienteRepository):
    cliente = await repo.buscar_por_correo(correo)
    if not cliente:
        return None, "credenciales_invalidas"

    if await repo.verificar_bloqueo(correo):
        ultimo_intento = cliente.ultimo_intento
        if ultimo_intento and ultimo_intento.tzinfo is None:
            ultimo_intento = ultimo_intento.replace(tzinfo=timezone.utc)
        tiempo_restante = 15 - int(
            (datetime.now(timezone.utc) - ultimo_intento).seconds / 60
        )
        return None, f"bloqueado:{tiempo_restante}"

    if not pwd_context.verify(password, cliente.password_hash):
        await repo.registrar_intento_fallido(correo)
        cliente_actualizado = await repo.buscar_por_correo(correo)
        if cliente_actualizado.intentos_fallidos >= 5:
            return None, "bloqueado:15"
        return None, "credenciales_invalidas"

    await repo.reset_intentos(correo)
    access_token = crear_token({"sub": str(cliente.id), "tipo": "access"}, timedelta(hours=24))
    refresh_token = crear_token({"sub": str(cliente.id), "tipo": "refresh"}, timedelta(days=7))
    return {"access_token": access_token, "refresh_token": refresh_token}, None