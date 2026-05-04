"""Sala repository."""

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.infrastructure.models.sala import Sala
from ..base_repository import AbstractRepository


class SalaRepository(AbstractRepository[Sala]):
    """Repositorio para entidades Sala."""

    def add(self, entity: Sala) -> Sala:
        """Crea una nueva sala."""
        self.db.add(entity)
        self.db.commit()
        return entity

    def get(self, entity_id: int) -> Sala | None:
        """Obtiene sala por ID."""
        stmt = select(Sala).where(Sala.id == entity_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 10) -> list[Sala]:
        """Lista todas las salas."""
        stmt = select(Sala).offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def update(self, entity_id: int, updates: dict) -> Sala | None:
        """Actualiza una sala por ID."""
        entity = self.get(entity_id)
        if not entity:
            return None
        
        for key, value in updates.items():
            setattr(entity, key, value)
        
        self.db.commit()
        return entity

    def delete(self, entity_id: int) -> bool:
        """Elimina una sala."""
        entity = self.get(entity_id)
        if not entity:
            return False
        
        self.db.delete(entity)
        self.db.commit()
        return True

    def exists(self, entity_id: int) -> bool:
        """Verifica si existe una sala."""
        stmt = select(func.count()).where(Sala.id == entity_id)
        result = self.db.scalar(stmt)
        return result > 0

    # Métodos específicos del negocio

    def contar_por_multiplex(self, multiplex_id: int) -> int:
        """Cuenta el número de salas en un multiplex."""
        stmt = select(func.count(Sala.id)).where(Sala.multiplexId == multiplex_id)
        count = self.db.scalar(stmt)
        return count or 0

    def obtener_por_multiplex(self, multiplex_id: int, skip: int = 0, limit: int = 10) -> list[Sala]:
        """Obtiene todas las salas de un multiplex."""
        stmt = select(Sala).where(Sala.multiplexId == multiplex_id).offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def obtener_por_numero(self, numero: int) -> Sala | None:
        """Obtiene sala por número."""
        stmt = select(Sala).where(Sala.numero == numero)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def desactivar(self, sala_id: int) -> Sala | None:
        """Desactiva una sala."""
        return self.update(sala_id, {"estaActiva": False})

    def activar(self, sala_id: int) -> Sala | None:
        """Activa una sala."""
        return self.update(sala_id, {"estaActiva": True})
