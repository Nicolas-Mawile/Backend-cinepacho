from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.configuracion import Configuracion
from app.infrastructure.base_repository import AbstractRepository


class ConfiguracionRepository(AbstractRepository[Configuracion]):
    """Repositorio para acceder a la configuración del sistema."""

    async def add(self, entity: Configuracion) -> Configuracion:
        self.db.add(entity)
        await self.commit()
        return entity

    async def get(self, entity_id: int) -> Configuracion | None:
        stmt = select(Configuracion).where(Configuracion.id == entity_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_por_clave(self, clave: str) -> Configuracion | None:
        """Obtiene configuración por clave (muy común)."""
        stmt = select(Configuracion).where(Configuracion.clave == clave)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[Configuracion]:
        stmt = select(Configuracion).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, entity_id: int, data: dict) -> Configuracion | None:
        entity = await self.get(entity_id)
        if not entity:
            return None
        for key, value in data.items():
            setattr(entity, key, value)
        await self.commit()
        return entity

    async def delete(self, entity_id: int) -> bool:
        entity = await self.get(entity_id)
        if not entity:
            return False
        await self.db.delete(entity)
        await self.commit()
        return True

    async def exists(self, entity_id: int) -> bool:
        stmt = select(Configuracion).where(Configuracion.id == entity_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None