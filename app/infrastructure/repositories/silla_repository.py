"""Silla repository."""
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.infrastructure.models.silla import Silla
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.boleta import Boleta
from ..base_repository import AbstractRepository

class SillaRepository(AbstractRepository[Silla]):
    """Repositorio para entidades Silla."""

    # =========================================================
    # CRUD
    # =========================================================
    def add(self, entity: Silla) -> Silla:
        self.db.add(entity)
        return entity

    def add_many(self, entities: list[Silla]) -> list[Silla]:
        self.db.add_all(entities)
        return entities

    def get(self, entity_id: int) -> Silla | None:
        stmt = (select(Silla).options(joinedload(Silla.tipoSilla)).where(Silla.id == entity_id))
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 10) -> list[Silla]:
        stmt = (select(Silla).offset(skip).limit(limit))
        result = self.db.execute(stmt)
        return result.scalars().all()

    def update(self, entity_id: int, updates: dict) -> Silla | None:
        entity = self.get(entity_id)
        if not entity:
            return None
        for key, value in updates.items():
            setattr(entity, key, value)
        return entity

    def delete(self, entity_id: int) -> bool:
        entity = self.get(entity_id)
        if not entity:
            return False
        self.db.delete(entity)
        return True

    def exists(self, entity_id: int) -> bool:
        stmt = (select(func.count()).select_from(Silla).where(Silla.id == entity_id))
        result = self.db.scalar(stmt)
        return result > 0

    # =========================================================
    # CONSULTAS DE NEGOCIO
    # =========================================================
    def contar_por_sala(self, sala_id: int) -> int:
        stmt = (select(func.count(Silla.id)).where(Silla.salaId == sala_id))
        count = self.db.scalar(stmt)
        return count or 0

    def contar_activas_por_sala(self, sala_id: int) -> int:
        stmt = (select(func.count(Silla.id)).where(Silla.salaId == sala_id, Silla.estaActiva.is_(True)))
        count = self.db.scalar(stmt)
        return count or 0

    def obtener_por_sala(self, sala_id: int, skip: int = 0, limit: int = 50) -> list[Silla]:
        stmt = (select(Silla).options(joinedload(Silla.tipoSilla)).where(Silla.salaId == sala_id).offset(skip).limit(limit))
        result = self.db.execute(stmt)
        return result.scalars().all()

    def obtener_por_multiplex(self, multiplex_id: int, skip: int = 0, limit: int = 100) -> list[Silla]:
        from app.infrastructure.models.sala import Sala
        stmt = (select(Silla).join(Sala).where(Sala.multiplexId == multiplex_id).offset(skip).limit(limit))
        result = self.db.execute(stmt)
        return result.scalars().all()

    # =========================================================
    # ACTIVACIÓN / DESACTIVACIÓN
    # =========================================================
    def desactivar(self, silla_id: int) -> Silla | None:
        return self.update(silla_id, {"estaActiva": False})

    def activar(self, silla_id: int) -> Silla | None:
        return self.update(silla_id, {"estaActiva": True})

    def desactivar_por_sala(self, sala_id: int) -> int:
        stmt = (select(Silla).where(Silla.salaId == sala_id, Silla.estaActiva.is_(True)))
        result = self.db.execute(stmt)
        sillas = result.scalars().all()
        for silla in sillas:
            silla.estaActiva = False

        return len(sillas)

    def desactivar_por_multiplex(self, multiplex_id: int) -> int:
        from app.infrastructure.models.sala import Sala
        stmt = (select(Silla).join(Sala).where(Sala.multiplexId == multiplex_id, Silla.estaActiva.is_(True)))
        result = self.db.execute(stmt)
        sillas = result.scalars().all()
        for silla in sillas:
            silla.estaActiva = False

        return len(sillas)

    # =========================================================
    # VALIDACIONES
    # =========================================================
    def tiene_boletas_vendidas(self, sala_id: int) -> bool:
        stmt = (select(func.count(Boleta.id)).join(Funcion).where(Funcion.salaId == sala_id))
        count = self.db.scalar(stmt)
        return (count or 0) > 0