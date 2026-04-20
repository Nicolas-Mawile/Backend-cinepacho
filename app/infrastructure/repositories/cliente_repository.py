"""Cliente repository."""
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cliente import Cliente

class ClienteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_correo(self, correo: str) -> Cliente | None:
        result = await self.session.execute(
            select(Cliente).where(Cliente.correo == correo)
        )
        return result.scalar_one_or_none()

    async def incrementar_intentos(self, cliente: Cliente) -> None:
        cliente.intentos_fallidos += 1
        cliente.ultimo_intento = datetime.now(timezone.utc)
        await self.session.commit()

    async def reset_intentos(self, cliente: Cliente) -> None:
        cliente.intentos_fallidos = 0
        cliente.ultimo_intento = None
        cliente.ultimo_login = datetime.now(timezone.utc)
        await self.session.commit()

    async def esta_bloqueado(self, cliente: Cliente) -> bool:
        if cliente.intentos_fallidos >= 5 and cliente.ultimo_intento:
            ultimo_intento = cliente.ultimo_intento
            if ultimo_intento.tzinfo is None:
                ultimo_intento = ultimo_intento.replace(tzinfo=timezone.utc)
            tiempo_transcurrido = datetime.now(timezone.utc) - ultimo_intento
            if tiempo_transcurrido < timedelta(minutes=15):
                return True
        return False