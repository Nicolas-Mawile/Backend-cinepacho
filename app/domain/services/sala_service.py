"""Servicio de gestión de salas."""

from sqlalchemy.orm import Session

from app.infrastructure.repositories.sala_repository import SalaRepository
from app.infrastructure.repositories.multiplex_repository import MultiplexRepository
from app.infrastructure.repositories.silla_repository import SillaRepository
from app.infrastructure.models.sala import Sala
from app.api.schemas.sala import SalaCreate, SalaUpdate
from app.domain.exceptions import (
    SalaNotFoundError,
    MultiplexNotFoundError,
    SalaLimitExceededError,
    DuplicateNumeroSalaError,
    SalaDependenciesError,
)


class SalaService:
    """Servicio para gestionar salas."""

    MAX_SALAS_POR_MULTIPLEX = 10

    def __init__(self, db: Session):
        """Inicializa el servicio con repositorios."""
        self.sala_repo = SalaRepository(db)
        self.multiplex_repo = MultiplexRepository(db)
        self.silla_repo = SillaRepository(db)
        self.db = db

    def validar_limite(self, multiplex_id: int) -> None:
        """
        Valida que no se haya alcanzado el límite de salas para el multiplex.
        
        Args:
            multiplex_id: ID del multiplex
            
        Raises:
            SalaLimitExceededError: Si se alcanzó el límite
        """
        cantidad_actual = self.sala_repo.contar_por_multiplex(multiplex_id)
        if cantidad_actual >= self.MAX_SALAS_POR_MULTIPLEX:
            raise SalaLimitExceededError(
                f"Límite de {self.MAX_SALAS_POR_MULTIPLEX} salas alcanzado "
                f"para el multiplex {multiplex_id}"
            )

    def validar_multiplex_existe(self, multiplex_id: int) -> None:
        """
        Valida que el multiplex existe.
        
        Args:
            multiplex_id: ID del multiplex
            
        Raises:
            MultiplexNotFoundError: Si el multiplex no existe
        """
        if not self.multiplex_repo.exists(multiplex_id):
            raise MultiplexNotFoundError(f"Multiplex {multiplex_id} no encontrado")

    def validar_numero_unico(self, numero: int, excluir_sala_id: int = None) -> None:
        """
        Valida que el número de sala sea único.
        
        Args:
            numero: Número de sala a validar
            excluir_sala_id: ID de sala a excluir de la validación (para updates)
            
        Raises:
            DuplicateNumeroSalaError: Si el número ya existe
        """
        sala_existente = self.sala_repo.obtener_por_numero(numero)
        if sala_existente and sala_existente.id != excluir_sala_id:
            raise DuplicateNumeroSalaError(
                f"El número de sala {numero} ya está en uso"
            )

    def crear_sala(self, multiplex_id: int, datos: SalaCreate) -> Sala:
        """
        Crea una nueva sala con validaciones.
        
        Args:
            multiplex_id: ID del multiplex propietario
            datos: Datos para crear la sala
            
        Returns:
            Sala: Sala creada
            
        Raises:
            MultiplexNotFoundError: Si el multiplex no existe
            SalaLimitExceededError: Si se alcanzó el límite de salas
            DuplicateNumeroSalaError: Si el número de sala ya existe
        """
        # Validaciones
        self.validar_multiplex_existe(multiplex_id)
        self.validar_limite(multiplex_id)
        self.validar_numero_unico(datos.numero)

        # Crear sala (estaActiva=True por defecto en el modelo)
        sala = Sala(
            numero=datos.numero,
            capacidadTotal=datos.capacidadTotal,
            capacidadPreferencial=datos.capacidadPreferencial,
            multiplexId=multiplex_id,
            estaActiva=True,  # Estado inicial
        )

        return self.sala_repo.add(sala)

    def obtener_sala(self, sala_id: int) -> Sala:
        """
        Obtiene una sala por ID.
        
        Args:
            sala_id: ID de la sala
            
        Returns:
            Sala: Sala encontrada
            
        Raises:
            SalaNotFoundError: Si la sala no existe
        """
        sala = self.sala_repo.get(sala_id)
        if not sala:
            raise SalaNotFoundError(f"Sala {sala_id} no encontrada")
        return sala

    def obtener_salas_multiplex(
        self, multiplex_id: int, skip: int = 0, limit: int = 10
    ) -> list[Sala]:
        """
        Obtiene todas las salas de un multiplex.
        
        Args:
            multiplex_id: ID del multiplex
            skip: Salas a saltar (paginación)
            limit: Límite de salas a retornar
            
        Returns:
            list[Sala]: Lista de salas
            
        Raises:
            MultiplexNotFoundError: Si el multiplex no existe
        """
        self.validar_multiplex_existe(multiplex_id)
        return self.sala_repo.obtener_por_multiplex(multiplex_id, skip, limit)

    def actualizar_sala(self, sala_id: int, datos: SalaUpdate) -> Sala:
        """
        Actualiza una sala.
        
        Args:
            sala_id: ID de la sala a actualizar
            datos: Datos a actualizar
            
        Returns:
            Sala: Sala actualizada
            
        Raises:
            SalaNotFoundError: Si la sala no existe
            DuplicateNumeroSalaError: Si el nuevo número ya existe
        """
        sala = self.obtener_sala(sala_id)

        # Validar número único si se está actualizando
        if datos.numero is not None:
            self.validar_numero_unico(datos.numero, excluir_sala_id=sala_id)

        # Preparar actualizaciones
        updates = datos.model_dump(exclude_none=True)
        sala_actualizada = self.sala_repo.update(sala_id, updates)

        if not sala_actualizada:
            raise SalaNotFoundError(f"Sala {sala_id} no encontrada")

        return sala_actualizada

    def eliminar_sala(self, sala_id: int) -> bool:
        """
        Elimina una sala. Valida dependencias primero.
        
        Args:
            sala_id: ID de la sala a eliminar
            
        Returns:
            bool: True si se eliminó, False si no existe
            
        Raises:
            SalaDependenciesError: Si la sala tiene sillas o funciones
        """
        # Verificar que la sala existe
        sala = self.obtener_sala(sala_id)
        
        # Validar que no tiene dependencias
        self.validar_sin_dependencias(sala_id)
        
        return self.sala_repo.delete(sala_id)

    def validar_sin_dependencias(self, sala_id: int) -> None:
        """
        Valida que una sala no tiene sillas ni funciones activas.
        
        Args:
            sala_id: ID de la sala
            
        Raises:
            SalaDependenciesError: Si tiene dependencias
        """
        # Contar sillas
        cantidad_sillas = self.silla_repo.contar_por_sala(sala_id)
        if cantidad_sillas > 0:
            raise SalaDependenciesError(
                f"No se puede eliminar la sala {sala_id}: tiene {cantidad_sillas} sillas. "
                "Desactive o elimine las sillas primero."
            )

    def tiene_dependencias(self, sala_id: int) -> dict:
        """
        Verifica si una sala tiene dependencias y retorna información.
        
        Args:
            sala_id: ID de la sala
            
        Returns:
            dict con:
                - "tiene_sillas": bool
                - "cantidad_sillas": int
                - "tiene_sillas_activas": int
                - "tiene_boletas": bool
                - "total_dependencias": int
        """
        cantidad_sillas = self.silla_repo.contar_por_sala(sala_id)
        cantidad_activas = self.silla_repo.contar_activas_por_sala(sala_id)
        tiene_boletas = self.silla_repo.tiene_boletas_vendidas(sala_id)
        
        return {
            "tiene_sillas": cantidad_sillas > 0,
            "cantidad_sillas": cantidad_sillas,
            "cantidad_sillas_activas": cantidad_activas,
            "tiene_boletas_vendidas": tiene_boletas,
            "total_dependencias": cantidad_sillas,
        }

    def cambiar_estado(self, sala_id: int, activo: bool) -> Sala:
        """
        Cambia el estado (activo/inactivo) de una sala.
        
        Args:
            sala_id: ID de la sala
            activo: Nuevo estado
            
        Returns:
            Sala: Sala con estado actualizado
            
        Raises:
            SalaNotFoundError: Si la sala no existe
        """
        sala = self.obtener_sala(sala_id)
        return self.sala_repo.update(sala_id, {"estaActiva": activo})
