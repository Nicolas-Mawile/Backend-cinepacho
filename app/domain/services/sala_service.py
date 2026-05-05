"""Servicio de gestión de salas."""

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.infrastructure.repositories.sala_repository import SalaRepository
from app.infrastructure.repositories.multiplex_repository import MultiplexRepository
from app.infrastructure.repositories.silla_repository import SillaRepository
from app.infrastructure.models.sala import Sala
from app.infrastructure.models.silla import Silla
from app.infrastructure.models.tipoSilla import TipoSilla
from app.api.schemas.sala import SalaCreate, SalaUpdate, SillaCreate
from app.domain.exceptions import (
    SalaNotFoundError,
    MultiplexNotFoundError,
    SalaLimitExceededError,
    DuplicateNumeroSalaError,
    SalaConfigurationError,
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

    def _normalizar_tipo_silla(self, tipo_silla: str) -> str:
        return tipo_silla.strip().capitalize()

    def _obtener_o_crear_tipo_silla(self, tipo_silla: str) -> int:
        nombre = self._normalizar_tipo_silla(tipo_silla)
        stmt = select(TipoSilla).where(func.lower(TipoSilla.nombre) == nombre.lower())
        result = self.db.execute(stmt)
        tipo = result.scalar_one_or_none()
        if tipo:
            return tipo.id

        tipo = TipoSilla(nombre=nombre, precio=0.0)
        self.db.add(tipo)
        self.db.commit()
        return tipo.id

    def _crear_sillas_para_sala(self, sala: Sala, sillas: list[SillaCreate]) -> None:
        silla_entities = []
        for item in sillas:
            tipo_id = self._obtener_o_crear_tipo_silla(item.tipo_silla)
            silla_entities.append(
                Silla(
                    fila=item.fila_silla,
                    columna=item.columna_silla,
                    salaId=sala.id,
                    tipoSillaId=tipo_id,
                    estaActiva=True,
                )
            )

        self.silla_repo.add_many(silla_entities)

    def generar_sillas_predeterminadas(self) -> list[SillaCreate]:
        """Genera la configuración de sillas predeterminada para una sala."""
        sillas: list[SillaCreate] = []
        for fila in range(1, 7):
            for columna in range(1, 11):
                tipo = "preferencial" if fila <= 2 else "regular"
                sillas.append(SillaCreate(tipo_silla=tipo, fila_silla=fila, columna_silla=columna))
        return sillas

    def crear_salas_predeterminadas(self, multiplex_id: int, cantidad: int = 5) -> list[Sala]:
        """Crea un conjunto de salas predeterminadas para un multiplex."""
        salas = []
        sillas_default = self.generar_sillas_predeterminadas()
        for _ in range(cantidad):
            numero = self.obtener_numero_disponible(multiplex_id)
            sala_datos = SalaCreate(
                numero=numero,
                capacidadTotal=60,
                capacidadPreferencial=20,
                sillas=sillas_default,
            )
            salas.append(self.crear_sala(multiplex_id, sala_datos))
        return salas

    def _validar_sillas(self, datos: SalaCreate | SalaUpdate, capacidad_total: int, capacidad_preferencial: int) -> None:
        if datos.sillas:
            if len(datos.sillas) != capacidad_total:
                raise SalaConfigurationError(
                    "La cantidad de sillas debe coincidir con capacidadTotal"
                )
            preferenciales = sum(
                1
                for item in datos.sillas
                if self._normalizar_tipo_silla(item.tipo_silla) == "Preferencial"
            )
            if preferenciales != capacidad_preferencial:
                raise SalaConfigurationError(
                    "La cantidad de sillas preferenciales debe coincidir con capacidadPreferencial"
                )

    def obtener_numero_disponible(self, multiplex_id: int) -> int:
        """Busca el siguiente número de sala disponible para el multiplex."""
        stmt = select(Sala.numero).where(Sala.multiplexId == multiplex_id).order_by(Sala.numero)
        resultado = self.db.execute(stmt).scalars().all()
        usados = set(resultado)
        for numero in range(1, 1000):
            if numero not in usados:
                return numero
        raise SalaConfigurationError("No quedan números disponibles para nuevas salas")

    
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

    def validar_numero_unico(self, numero: int, multiplex_id: int, excluir_sala_id: int = None) -> None:
        """
        Valida que el número de sala sea único en el multiplex.
        
        Args:
            numero: Número de sala a validar
            multiplex_id: ID del multiplex
            excluir_sala_id: ID de sala a excluir de la validación (para updates)
            
        Raises:
            DuplicateNumeroSalaError: Si el número ya existe en el multiplex
        """
        sala_existente = self.sala_repo.obtener_por_numero(numero, multiplex_id)
        if sala_existente and sala_existente.id != excluir_sala_id:
            raise DuplicateNumeroSalaError(
                f"El número de sala {numero} ya está en uso en este multiplex"
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
            SalaConfigurationError: Si la configuración de sillas es inconsistente
        """
        self.validar_multiplex_existe(multiplex_id)
        self.validar_limite(multiplex_id)

        numero = datos.numero if datos.numero is not None else self.obtener_numero_disponible(multiplex_id)
        self.validar_numero_unico(numero, multiplex_id)

        self._validar_sillas(datos, datos.capacidadTotal, datos.capacidadPreferencial)

        sala = Sala(
            numero=numero,
            capacidadTotal=datos.capacidadTotal,
            capacidadPreferencial=datos.capacidadPreferencial,
            multiplexId=multiplex_id,
            estaActiva=True,
        )

        sala = self.sala_repo.add(sala)

        if datos.sillas:
            self._crear_sillas_para_sala(sala, datos.sillas)

        return sala

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
    
    def _sync_sillas(
        self,
        sala: Sala,
        sillas_input: list[SillaCreate],
        capacidad_total: int,
        capacidad_pref: int
    ):
        input_map = {
            (s.fila_silla, s.columna_silla): s
            for s in sillas_input
        }

        if len(input_map) != len(sillas_input):
            raise SalaConfigurationError("Sillas duplicadas en request")

        total = len(sillas_input)
        preferenciales = sum(
            1 for s in sillas_input if s.tipo_silla.lower() == "preferencial"
        )

        if total != capacidad_total:
            raise SalaConfigurationError(
                f"Cantidad de sillas ({total}) no coincide con capacidadTotal ({capacidad_total})"
            )

        if preferenciales != capacidad_pref:
            raise SalaConfigurationError(
                f"Preferenciales ({preferenciales}) no coincide con capacidadPreferencial ({capacidad_pref})"
            )

        existentes = {
            (s.fila, s.columna): s
            for s in sala.sillas
        }

        tipos_map = self._mapear_tipos()


        for key, silla_data in input_map.items():

            tipo = tipos_map.get(silla_data.tipo_silla.lower())
            if not tipo:
                raise SalaConfigurationError(
                    f"Tipo inválido: {silla_data.tipo_silla}"
                )

            if key in existentes:
                silla = existentes[key]

                silla.tipoSilla = tipo
                silla.estaActiva = True

            else:
                nueva = Silla(
                    salaId=sala.id,
                    fila=silla_data.fila_silla,
                    columna=silla_data.columna_silla,
                    tipoSilla=tipo,
                    estaActiva=True
                )
                self.db.add(nueva)

        for key, silla in existentes.items():
            if key not in input_map:
                silla.estaActiva = False
                
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
        sala = self.sala_repo.get_with_sillas(sala_id)

        if not sala:
            raise SalaNotFoundError()

        if datos.numero is not None:
            sala.numero = datos.numero

        if datos.capacidadTotal is not None:
            sala.capacidadTotal = datos.capacidadTotal

        if datos.capacidadPreferencial is not None:
            sala.capacidadPreferencial = datos.capacidadPreferencial

        if datos.sillas is not None:
            self._sync_sillas(
                sala,
                datos.sillas,
                sala.capacidadTotal,
                sala.capacidadPreferencial
            )

        self.db.commit()
        self.db.refresh(sala)

        return sala

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
        sala = self.obtener_sala(sala_id)
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
    
    def _mapear_tipos(self):
        from app.infrastructure.models.tipoSilla import TipoSilla

        stmt = select(TipoSilla)
        tipos = self.db.execute(stmt).scalars().all()

        return {t.nombre.lower(): t for t in tipos}