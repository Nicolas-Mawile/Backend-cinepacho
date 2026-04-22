"""Cliente repository."""
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.base_repository import AbstractRepository
from app.models.cliente import Cliente


class ClienteRepository(AbstractRepository[Cliente]):
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Métodos base de AbstractRepository ───────────────────────────────

    async def add(self, entity: Cliente) -> Cliente:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get(self, entity_id: int) -> Cliente | None:
        result = await self.session.execute(
            select(Cliente).where(Cliente.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def list(self) -> list[Cliente]:
        result = await self.session.execute(select(Cliente))
        return list(result.scalars().all())

    async def remove(self, entity: Cliente) -> None:
        await self.session.delete(entity)
        await self.session.commit()

    # ── Métodos específicos de la tarea ──────────────────────────────────

    async def crear(self, datos_cliente: dict) -> Cliente:
        cliente = Cliente(**datos_cliente)
        return await self.add(cliente)

    async def buscar_por_correo(self, correo: str) -> Cliente | None:
        result = await self.session.execute(
            select(Cliente).where(Cliente.correo == correo)
        )
        return result.scalar_one_or_none()

    async def buscar_por_id(self, id: int) -> Cliente | None:
        return await self.get(id)

    async def existe_correo(self, correo: str) -> bool:
        cliente = await self.buscar_por_correo(correo)
        return cliente is not None

    async def actualizar_puntos(self, id: int, delta_puntos: int) -> Cliente:
        cliente = await self.get(id)
        if cliente is None:
            raise ValueError(f"Cliente con id {id} no existe")
        cliente.puntos = (cliente.puntos or 0) + delta_puntos
        await self.session.commit()
        await self.session.refresh(cliente)
        return cliente

    async def registrar_intento_fallido(self, correo: str) -> None:
        cliente = await self.buscar_por_correo(correo)
        if cliente is None:
            return
        cliente.intentos_fallidos = (cliente.intentos_fallidos or 0) + 1
        cliente.ultimo_intento = datetime.now(timezone.utc)
        await self.session.commit()

    async def reset_intentos(self, correo: str) -> None:
        cliente = await self.buscar_por_correo(correo)
        if cliente is None:
            return
        cliente.intentos_fallidos = 0
        cliente.ultimo_intento = None
        cliente.ultimo_login = datetime.now(timezone.utc)
        await self.session.commit()

    async def verificar_bloqueo(self, correo: str) -> bool:
        cliente = await self.buscar_por_correo(correo)
        if cliente is None:
            return False
        if cliente.intentos_fallidos >= 5 and cliente.ultimo_intento:
            ultimo = cliente.ultimo_intento
            if ultimo.tzinfo is None:
                ultimo = ultimo.replace(tzinfo=timezone.utc)
            tiempo_transcurrido = datetime.now(timezone.utc) - ultimo
            return tiempo_transcurrido < timedelta(minutes=15)
        return False