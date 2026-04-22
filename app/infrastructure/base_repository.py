"""Abstract repository base class following Repository Pattern."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    """
    Clase base abstracta para todos los repositorios.
    Define el contrato que deben cumplir los repositorios específicos.
    
    Tipos:
        T: Tipo genérico que representa la entidad a persistir
    """
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa el repositorio con una sesión de BD.
        
        Args:
            db: Sesión asincrónica de SQLAlchemy
        """
        self.db = db
    
    @abstractmethod
    async def add(self, entity: T) -> T:
        """
        Agrega una nueva entidad a la BD.
        
        Args:
            entity: Entidad a crear
            
        Returns:
            La entidad creada con ID asignado
        """
        pass
    
    @abstractmethod
    async def get(self, entity_id: int) -> Optional[T]:
        """
        Obtiene una entidad por su ID.
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            La entidad o None si no existe
        """
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 10) -> List[T]:
        """
        Lista todas las entidades con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Máximo de registros a retornar
            
        Returns:
            Lista de entidades
        """
        pass
    
    @abstractmethod
    async def update(self, entity_id: int, data: dict) -> Optional[T]:
        """
        Actualiza una entidad existente.
        
        Args:
            entity_id: ID de la entidad a actualizar
            data: Diccionario con los campos a actualizar
            
        Returns:
            La entidad actualizada o None si no existe
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """
        Elimina una entidad por su ID.
        
        Args:
            entity_id: ID de la entidad a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        pass
    
    @abstractmethod
    async def exists(self, entity_id: int) -> bool:
        """
        Verifica si una entidad existe.
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            True si existe, False en caso contrario
        """
        pass
    
    async def commit(self):
        """Confirma los cambios en la BD."""
        await self.db.commit()
    
    async def rollback(self):
        """Revierte los cambios no confirmados."""
        await self.db.rollback()
