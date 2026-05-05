"""Empleado repository."""

from sqlalchemy import select, func
from app.infrastructure.models.empleado import Empleado
from ..base_repository import AbstractRepository


class EmpleadoRepository(AbstractRepository[Empleado]):
    """Repositorio para la entidad Empleado."""

    def add(self, entity: Empleado) -> Empleado:
        """Agrega un nuevo empleado."""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get(self, entity_id: int) -> Empleado | None:
        """Obtiene un empleado por ID."""
        stmt = select(Empleado).where(Empleado.id == entity_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 10, multiplex_id: int | None = None) -> list[Empleado]:
        """Lista empleados con paginación y filtro opcional por multiplex."""
        stmt = select(Empleado)
        if multiplex_id:
            stmt = stmt.where(Empleado.multiplex_id == multiplex_id)
        
        stmt = stmt.offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def count(self, multiplex_id: int | None = None) -> int:
        """Cuenta el total de empleados con filtro opcional por multiplex."""
        stmt = select(func.count(Empleado.id))
        if multiplex_id:
            stmt = stmt.where(Empleado.multiplex_id == multiplex_id)
        return self.db.scalar(stmt) or 0

    def update(self, entity_id: int, updates: dict) -> Empleado | None:
        """Actualiza un empleado."""
        entity = self.get(entity_id)
        if not entity:
            return None
        
        for key, value in updates.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity_id: int) -> bool:
        """Deshabilita un empleado (soft delete)."""
        entity = self.get(entity_id)
        if not entity:
            return False
        
        entity.activo = False
        self.db.commit()
        return True

    def exists(self, entity_id: int) -> bool:
        """Verifica existencia por ID."""
        stmt = select(func.count()).where(Empleado.id == entity_id)
        result = self.db.scalar(stmt)
        return result > 0

    def buscar_por_cedula(self, cedula: str) -> Empleado | None:
        """Busca un empleado por su cédula."""
        stmt = select(Empleado).where(Empleado.cedula == cedula)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
