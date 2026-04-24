from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from decimal import Decimal

from app.models.multiplex import Multiplex
from app.models.sala import Sala
from app.infrastructure.base_repository import AbstractRepository


class MultiplexRepository(AbstractRepository[Multiplex]):
    """Repositorio para entidades Multiplex."""

    async def add(self, entity: Multiplex) -> Multiplex:
        """Crea un nuevo multiplex."""
        self.db.add(entity)
        await self.commit()
        return entity

    async def get(self, entity_id: str) -> Multiplex | None:
        """Obtiene multiplex por ID."""
        stmt = select(Multiplex).where(Multiplex.id == entity_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 10, ciudad: str = None) -> list[Multiplex]:
        """Lista multiplexes con filtros opcionales."""
        stmt = select(Multiplex)
        
        if ciudad:
            stmt = stmt.where(Multiplex.ciudad == ciudad)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, entity_id: str, data: dict) -> Multiplex | None:
        """Actualiza un multiplex."""
        entity = await self.get(entity_id)
        if not entity:
            return None
        
        for key, value in data.items():
            setattr(entity, key, value)
        
        await self.commit()
        return entity

    async def delete(self, entity_id: str) -> bool:
        """Elimina un multiplex."""
        entity = await self.get(entity_id)
        if not entity:
            return False
        
        await self.db.delete(entity)
        await self.commit()
        return True

    async def exists(self, entity_id: str) -> bool:
        """Verifica si existe un multiplex."""
        stmt = select(func.count()).where(Multiplex.id == entity_id)
        result = await self.db.scalar(stmt)
        return result > 0

    # Métodos específicos del negocio
    async def tiene_dependencias(self, multiplex_id: str) -> bool:
        """Verifica si el multiplex tiene salas."""
        stmt = select(func.count(Sala.id)).where(Sala.multiplex_id == multiplex_id)
        count = await self.db.scalar(stmt)
        return count > 0

    async def desactivar(self, multiplex_id: str) -> Multiplex | None:
        """Desactiva un multiplex."""
        return await self.update(multiplex_id, {"activo": False})

    # Alias para compatibilidad con tests
    async def crear(self, entity: Multiplex) -> Multiplex:
        """Alias de add() para compatibilidad."""
        return await self.add(entity)

    async def listar(self, skip: int = 0, limite: int = 10, ciudad: Optional[str] = None, activo: Optional[bool] = None) -> list[Multiplex]:
        """Alias de list() con parámetro ciudad."""
        return await self.list(skip, limite, ciudad)

    async def buscar_por_codigo(self, entity_codigo: str) -> Multiplex | None:
        """Busca un multiplex por su código."""
        stmt = select(Multiplex).where(Multiplex.codigo == entity_codigo)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()