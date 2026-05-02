from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.models.sala import Sala
from app.infrastructure.base_repository import AbstractRepository


class MultiplexRepository(AbstractRepository[Multiplex]):
    """Repositorio para entidades Multiplex."""

    def add(self, entity: Multiplex) -> Multiplex:
        """Crea un nuevo multiplex."""
        self.db.add(entity)
        self.db.commit()
        return entity

    def get(self, entity_id: int) -> Multiplex | None:
        """Obtiene multiplex por ID."""
        stmt = select(Multiplex).where(Multiplex.id == entity_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def list(self, skip: int = 0, limit: int = 10, ciudad: str = None, activo: bool = None) -> list[Multiplex]:
        """Lista multiplexes con filtros opcionales."""
        stmt = select(Multiplex)
        
        if ciudad:
            stmt = stmt.where(Multiplex.ciudad == ciudad)
        
        if activo is not None:
            stmt = stmt.where(Multiplex.estaActivo == activo)
        
        stmt = stmt.offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def update(self, entity_id: int | str, updates: dict) -> Multiplex | None:
        """Actualiza un multiplex por ID."""
        entity_id_int = int(entity_id) if isinstance(entity_id, str) else entity_id
        stmt = select(Multiplex).where(Multiplex.id == entity_id_int)
        result = self.db.execute(stmt)
        entity = result.scalar_one_or_none()
        
        if not entity:
            return None
        
        for key, value in updates.items():
            if key == "activo":
                setattr(entity, "estaActivo", value)
            else:
                setattr(entity, key, value)
        
        self.db.commit()
        return entity

    def delete(self, entity_id: int) -> bool:
        """Elimina un multiplex."""
        entity = self.get(entity_id)
        if not entity:
            return False

        self.db.delete(entity)
        self.db.commit()
        return True

    def exists(self, entity_id: int) -> bool:
        """Verifica si existe un multiplex."""
        stmt = select(func.count()).where(Multiplex.id == entity_id)
        result = self.db.scalar(stmt)
        return result > 0

    # Métodos específicos del negocio
    def tiene_dependencias(self, multiplex_id: int | str) -> bool:
        """Verifica si el multiplex tiene salas."""
        multiplex_id_int = int(multiplex_id) if isinstance(multiplex_id, str) else multiplex_id
        stmt = select(func.count(Sala.id)).where(Sala.multiplexId == multiplex_id_int)
        count = self.db.scalar(stmt)
        return count > 0

    def desactivar(self, multiplex_id: int | str) -> Multiplex | None:
        """Desactiva un multiplex."""
        return self.update(multiplex_id, {"activo": False})

    # Alias para compatibilidad con tests
    def crear(self, entity: Multiplex) -> Multiplex:
        """Alias de add() para compatibilidad."""
        return self.add(entity)

    def listar(self, skip: int = 0, limite: int = 10, ciudad: Optional[str] = None, activo: Optional[bool] = None) -> list[Multiplex]:
        """Alias de list() con parámetro ciudad."""
        return self.list(skip, limite, ciudad, activo)

    def buscar_por_codigo(self, codigo: str) -> Multiplex | None:
        """Busca un multiplex por su código."""
        stmt = select(Multiplex).where(Multiplex.codigo == codigo)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def buscar_por_id(self, id: int | str) -> Multiplex | None:
        """Busca un multiplex por su ID."""
        id_int = int(id) if isinstance(id, str) else id
        stmt = select(Multiplex).where(Multiplex.id == id_int)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()