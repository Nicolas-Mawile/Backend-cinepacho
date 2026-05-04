"""Silla repository."""

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.infrastructure.models.silla import Silla
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.boleta import Boleta
from ..base_repository import AbstractRepository


class SillaRepository(AbstractRepository[Silla]):
    """Repositorio para entidades Silla."""

    def add(self, entity: Silla) -> Silla:
        """Crea una nueva silla."""
        self.db.add(entity)
        self.db.commit()
        return entity

    def get(self, entity_id: int) -> Silla | None:
        """Obtiene silla por ID."""
        stmt = select(Silla).where(Silla.id == entity_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 10) -> list[Silla]:
        """Lista todas las sillas."""
        stmt = select(Silla).offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def update(self, entity_id: int, updates: dict) -> Silla | None:
        """Actualiza una silla por ID."""
        entity = self.get(entity_id)
        if not entity:
            return None
        
        for key, value in updates.items():
            setattr(entity, key, value)
        
        self.db.commit()
        return entity

    def delete(self, entity_id: int) -> bool:
        """Elimina una silla."""
        entity = self.get(entity_id)
        if not entity:
            return False
        
        self.db.delete(entity)
        self.db.commit()
        return True

    def exists(self, entity_id: int) -> bool:
        """Verifica si existe una silla."""
        stmt = select(func.count()).where(Silla.id == entity_id)
        result = self.db.scalar(stmt)
        return result > 0

    # Métodos específicos del negocio

    def contar_por_sala(self, sala_id: int) -> int:
        """Cuenta el número de sillas en una sala."""
        stmt = select(func.count(Silla.id)).where(Silla.salaId == sala_id)
        count = self.db.scalar(stmt)
        return count or 0

    def contar_activas_por_sala(self, sala_id: int) -> int:
        """Cuenta el número de sillas activas en una sala."""
        stmt = select(func.count(Silla.id)).where(
            (Silla.salaId == sala_id) & (Silla.estaActiva == True)
        )
        count = self.db.scalar(stmt)
        return count or 0

    def obtener_por_sala(self, sala_id: int, skip: int = 0, limit: int = 50) -> list[Silla]:
        """Obtiene todas las sillas de una sala."""
        stmt = select(Silla).where(Silla.salaId == sala_id).offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def obtener_por_multiplex(self, multiplex_id: int, skip: int = 0, limit: int = 100) -> list[Silla]:
        """Obtiene todas las sillas de un multiplex (through salas)."""
        from app.infrastructure.models.sala import Sala
        
        stmt = select(Silla).join(Sala).where(
            Sala.multiplexId == multiplex_id
        ).offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def desactivar_por_multiplex(self, multiplex_id: int) -> int:
        """Desactiva todas las sillas de un multiplex. Retorna cantidad desactivada."""
        from app.infrastructure.models.sala import Sala
        
        # Obtener todas las sillas del multiplex que están activas
        stmt = select(Silla).join(Sala).where(
            (Sala.multiplexId == multiplex_id) & (Silla.estaActiva == True)
        )
        result = self.db.execute(stmt)
        sillas = result.scalars().all()
        
        # Desactivar cada silla
        for silla in sillas:
            silla.estaActiva = False
        
        self.db.commit()
        return len(sillas)

    def desactivar_por_sala(self, sala_id: int) -> int:
        """Desactiva todas las sillas de una sala. Retorna cantidad desactivada."""
        stmt = select(Silla).where(
            (Silla.salaId == sala_id) & (Silla.estaActiva == True)
        )
        result = self.db.execute(stmt)
        sillas = result.scalars().all()
        
        for silla in sillas:
            silla.estaActiva = False
        
        self.db.commit()
        return len(sillas)

    def desactivar(self, silla_id: int) -> Silla | None:
        """Desactiva una silla."""
        return self.update(silla_id, {"estaActiva": False})

    def activar(self, silla_id: int) -> Silla | None:
        """Activa una silla."""
        return self.update(silla_id, {"estaActiva": True})

    def tiene_boletas_vendidas(self, sala_id: int) -> bool:
        """Verifica si hay boletas vendidas en una sala (through funciones)."""
        stmt = select(func.count(Boleta.id)).join(Funcion).where(
            Funcion.salaId == sala_id
        )
        count = self.db.scalar(stmt)
        return count and count > 0
