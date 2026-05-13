"""Cliente repository."""

from sqlalchemy import select, func, update
from datetime import datetime, timedelta, timezone
from app.infrastructure.models.cliente import Cliente
from ..base_repository import AbstractRepository


class ClienteRepository(AbstractRepository[Cliente]):
    """Repositorio para la entidad Cliente."""

    def add(self, entity: Cliente) -> Cliente:
        """Agrega un nuevo cliente."""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get(self, entity_id: int) -> Cliente | None:
        """Obtiene un cliente por ID."""
        stmt = select(Cliente).where(Cliente.id == entity_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 10) -> list[Cliente]:
        """Lista clientes con paginación."""
        stmt = select(Cliente).offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def update(self, entity_id: int, updates: dict) -> Cliente | None:
        """Actualiza un cliente."""
        entity = self.get(entity_id)
        if not entity:
            return None
        
        for key, value in updates.items():
            setattr(entity, key, value)
        
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity_id: int) -> bool:
        """Elimina un cliente."""
        entity = self.get(entity_id)
        if not entity:
            return False
        
        self.db.delete(entity)
        self.db.commit()
        return True

    def exists(self, entity_id: int) -> bool:
        """Verifica existencia por ID."""
        stmt = select(func.count()).where(Cliente.id == entity_id)
        result = self.db.scalar(stmt)
        return result > 0

    # Métodos específicos de la tarea ST-03

    def crear(self, datos_cliente: dict) -> Cliente:
        """Crea un cliente a partir de un diccionario."""
        nuevo_cliente = Cliente(**datos_cliente)
        return self.add(nuevo_cliente)

    def buscar_por_correo(self, correo: str) -> Cliente | None:
        """Busca un cliente por su correo electrónico."""
        stmt = select(Cliente).where(Cliente.correo == correo)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def buscar_por_id(self, entity_id: int) -> Cliente | None:
        """Alias de get() para cumplir con la interfaz solicitada."""
        return self.get(entity_id)

    def existe_correo(self, correo: str) -> bool:
        """Verifica si ya existe un cliente con ese correo."""
        stmt = select(func.count()).where(Cliente.correo == correo)
        result = self.db.scalar(stmt)
        return result > 0

    def actualizar_puntos(self, entity_id: int, delta_puntos: int) -> Cliente:
        """Actualiza los puntos acumulados de un cliente."""
        entity = self.get(entity_id)
        if not entity:
            raise ValueError(f"Cliente con id {entity_id} no encontrado")
        
        entity.puntos_acumulados += delta_puntos
        self.db.commit()
        self.db.refresh(entity)
        return entity
