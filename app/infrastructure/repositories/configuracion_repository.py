from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models.configuracion import Configuracion
from app.infrastructure.base_repository import AbstractRepository


class ConfiguracionRepository(AbstractRepository[Configuracion]):
    """Repositorio para acceder a la configuración del sistema."""

    def add(self, entity: Configuracion) -> Configuracion:
        self.db.add(entity)
        self.commit()
        return entity

    def get(self, entity_id: int) -> Configuracion | None:
        stmt = select(Configuracion).where(Configuracion.id == entity_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_por_clave(self, clave: str) -> Configuracion | None:
        """Obtiene configuración por clave (muy común)."""
        stmt = select(Configuracion).where(Configuracion.clave == clave)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def list(self, skip: int = 0, limit: int = 100) -> list[Configuracion]:
        stmt = select(Configuracion).offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def update(self, entity_id: int, data: dict) -> Configuracion | None:
        entity = self.get(entity_id)
        if not entity:
            return None
        for key, value in data.items():
            setattr(entity, key, value)
        self.commit()
        return entity

    def delete(self, entity_id: int) -> bool:
        entity = self.get(entity_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.commit()
        return True

    def exists(self, entity_id: int) -> bool:
        stmt = select(Configuracion).where(Configuracion.id == entity_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none() is not None