"""Servicio de funciones."""

from datetime import timedelta, datetime

from app.domain.exceptions import (
    FuncionNotFoundError,
    FuncionValidationError,
    MultiplexNotFoundError,
    SalaNotFoundError,
)
from app.api.schemas.funcion import FuncionCreate, FuncionUpdate
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.repositories.funcion_repository import FuncionRepository
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum


class FuncionService:
    def __init__(self, db):
        self.repo = FuncionRepository(db)

    def crear_funcion(self, data: FuncionCreate) -> Funcion:
        sala = self.repo.get_sala(data.salaId)
        if not sala or not sala.estaActiva:
            raise SalaNotFoundError("Sala no encontrada o inactiva")

        pelicula = self.repo.get_pelicula(data.peliculaId)
        if not pelicula or not pelicula.estaActiva:
            raise FuncionValidationError("Pelicula no encontrada o inactiva")

        if not self.repo.pelicula_en_cartelera(data.peliculaId, sala.multiplexId):
            raise FuncionValidationError("La pelicula no esta en la cartelera de este multiplex")

        fecha_fin = data.fechaHora + timedelta(minutes=pelicula.duracionMinutos)

        if self.repo.hay_solapamiento(data.salaId, data.fechaHora, fecha_fin):
            raise FuncionValidationError("Ya existe una funcion programada en ese horario para esta sala")

        funcion = Funcion(
            peliculaId=data.peliculaId,
            salaId=data.salaId,
            fechaHora=data.fechaHora,
            fechaHoraFin=fecha_fin,
            estaActiva=True,
        )
        creada = self.repo.add(funcion)
        return self.repo.get_detallada(creada.id) or creada

    def listar_por_pelicula(self, pelicula_id: int):
        if not self.repo.get_pelicula(pelicula_id):
            raise FuncionNotFoundError("Pelicula no encontrada")
        return self.repo.listar_por_pelicula(pelicula_id)

    def listar_por_multiplex(self, multiplex_id: int):
        if not self.repo.get_multiplex(multiplex_id):
            raise MultiplexNotFoundError("Multiplex no encontrado")
        return self.repo.listar_por_multiplex(multiplex_id)

    def listar_por_sala(self, sala_id: int):
        if not self.repo.get_sala(sala_id):
            raise SalaNotFoundError("Sala no encontrada")
        return self.repo.listar_por_sala(sala_id)

    def listar_por_pelicula_y_multiplex(self, multiplex_id: int, pelicula_id: int):
        if not self.repo.get_multiplex(multiplex_id):
            raise MultiplexNotFoundError("Multiplex no encontrado")
        if not self.repo.get_pelicula(pelicula_id):
            raise FuncionNotFoundError("Pelicula no encontrada")
        return self.repo.listar_por_pelicula_y_multiplex(multiplex_id, pelicula_id)
    
    def obtener_por_id(self, funcion_id: int):
        funcion = self.repo.get_by_id(funcion_id)

        if not funcion:
            raise FuncionNotFoundError("Función no encontrada")

        sillas_response = []
        for silla in funcion.sala.sillas:
            boleta_activa = None
            for boleta in silla.boletas:
                if boleta.funcionId != funcion.id:
                    continue
                detalle = boleta.detalle
                if detalle:
                    factura = detalle.factura
                    # PAGADA -> ocupada
                    if factura.estadoFactura == EstadoFacturaEnum.PAGADA:
                        boleta_activa = "OCUPADA"
                    # RESERVADA y no expirada
                    elif (factura.estadoFactura == EstadoFacturaEnum.RESERVADA and factura.fechaExpiracionReserva > datetime.utcnow()):
                        boleta_activa = "RESERVADA"
            estado = boleta_activa or "DISPONIBLE"
            sillas_response.append({"sillaId": silla.id,
                                    "fila": silla.fila,
                                    "columna": silla.columna,
                                    "tipo": silla.tipoSilla.nombre if silla.tipoSilla else None,
                                    "estado": estado,})

        return {"id": funcion.id,
                "peliculaId": funcion.peliculaId,
                "salaId": funcion.salaId,
                "fechaHora": funcion.fechaHora,
                "fechaHoraFin": funcion.fechaHoraFin,
                "estaActiva": funcion.estaActiva,
                "pelicula": funcion.pelicula,
                "sala": funcion.sala,
                "sillas": sillas_response,}

    def editar_funcion(self, funcion_id: int, data: FuncionUpdate) -> Funcion:
        funcion = self.repo.get(funcion_id)
        if not funcion:
            raise FuncionNotFoundError("Funcion no encontrada")

        if self.repo.tiene_boletas(funcion_id):
            raise FuncionValidationError("No se puede editar: la funcion tiene dependencias")

        nueva_sala_id = data.salaId if data.salaId is not None else funcion.salaId
        nueva_pelicula_id = data.peliculaId if data.peliculaId is not None else funcion.peliculaId
        nueva_fecha_hora = data.fechaHora if data.fechaHora is not None else funcion.fechaHora

        sala = self.repo.get_sala(nueva_sala_id)
        if not sala or not sala.estaActiva:
            raise SalaNotFoundError("Sala no encontrada o inactiva")

        pelicula = self.repo.get_pelicula(nueva_pelicula_id)
        if not pelicula or not pelicula.estaActiva:
            raise FuncionValidationError("Pelicula no encontrada o inactiva")

        if not self.repo.pelicula_en_cartelera(nueva_pelicula_id, sala.multiplexId):
            raise FuncionValidationError("La pelicula no esta en la cartelera de este multiplex")

        nueva_fecha_fin = nueva_fecha_hora + timedelta(minutes=pelicula.duracionMinutos)
        if self.repo.hay_solapamiento(nueva_sala_id, nueva_fecha_hora, nueva_fecha_fin, excluir_id=funcion_id):
            raise FuncionValidationError("Ya existe una funcion programada en ese horario para esta sala")

        cambios = {
            "salaId": nueva_sala_id,
            "peliculaId": nueva_pelicula_id,
            "fechaHora": nueva_fecha_hora,
            "fechaHoraFin": nueva_fecha_fin,
        }

        actualizada = self.repo.update(funcion_id, cambios)
        return self.repo.get_detallada(actualizada.id) if actualizada else None

    def eliminar_funcion(self, funcion_id: int) -> bool:
        funcion = self.repo.get(funcion_id)
        if not funcion:
            raise FuncionNotFoundError("Funcion no encontrada")
        if self.repo.tiene_boletas(funcion_id):
            raise FuncionValidationError("No se puede eliminar: la funcion tiene boletas vendidas")
        return self.repo.delete(funcion_id)