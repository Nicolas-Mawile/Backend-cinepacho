from datetime import datetime, timezone
from sqlalchemy import cast, Date
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.infrastructure.models.evaluacion import (
    Evaluacion
)
from app.infrastructure.models.boleta import Boleta
from app.infrastructure.models.factura import (
    Factura
)
from app.utils.timezone import nowNaive

from app.infrastructure.models.funcion import (
    Funcion
)

from app.infrastructure.models.detalleFactura import (
    DetalleFactura
)

from app.infrastructure.repositories.evaluacion_repository import (
    EvaluacionRepository
)
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum

class EvaluacionService:

    def __init__(
        self,
        db: Session
    ):

        self.db = db

        self.repository = (
            EvaluacionRepository(db)
        )

    # =====================================
    # EVALUAR PELÍCULA
    # =====================================

    def evaluar_pelicula(
        self,
        cliente_id: int,
        funcion_id: int,
        pelicula_id: int,
        puntuacion: int,
        comentario: str
    ):

        # =================================
        # VALIDAR PUNTUACIÓN
        # =================================

        if puntuacion < 1 or puntuacion > 5:

            raise HTTPException(
                status_code=400,
                detail=(
                    "La puntuación "
                    "debe ser entre 1 y 5"
                )
            )

        # =================================
        # JUSTIFICACIÓN BAJA
        # =================================

        if puntuacion <= 1 and not comentario:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Debe ingresar "
                    "una justificación"
                )
            )

        # =================================
        # VALIDAR FUNCIÓN
        # =================================

        funcion = (
            self.db.query(Funcion)
            .filter(Funcion.id == funcion_id)
            .first()
        )

        if not funcion:

            raise HTTPException(
                status_code=404,
                detail="Función no encontrada"
            )

        # =================================
        # VALIDAR PELÍCULA
        # =================================

        if funcion.peliculaId != pelicula_id:

            raise HTTPException(
                status_code=400,
                detail=(
                    "La película no "
                    "corresponde a la función"
                )
            )

        # =================================
        # VALIDAR FUNCIÓN FINALIZADA
        # =================================

        if (funcion.fechaHoraFin > nowNaive()):

            raise HTTPException(
                status_code=400,
                detail=(
                    "La función aún "
                    "no ha terminado"
                )
            )

        # =================================
        # VALIDAR COMPRA
        # =================================

        detalle = (
            self.db.query(DetalleFactura)
            .join(Factura, DetalleFactura.facturaId == Factura.id)
            .filter(
                DetalleFactura.boleta.has(
                    funcionId=funcion_id
                ),
                Factura.clienteId == cliente_id,
                Factura.estadoFactura == EstadoFacturaEnum.PAGADA,
            )
            .first()
        )

        if not detalle:

            raise HTTPException(
                status_code=403,
                detail=(
                    "Debe haber comprado "
                    "una boleta"
                )
            )

        # =================================
        # EVITAR DUPLICADOS
        # =================================

        existente = (
            self.repository
            .existe_evaluacion_pelicula(
                cliente_id,
                funcion_id,
                pelicula_id
            )
        )

        if existente:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Ya evaluó esta película"
                )
            )

        evaluacion = Evaluacion(
            cliente_id=cliente_id,
            funcion_id=funcion_id,
            pelicula_id=pelicula_id,
            puntuacion=puntuacion,
            comentario=comentario
        )

        return self.repository.add(
            evaluacion
        )
    
        # =====================================
    # EVALUAR SERVICIO / SNACK
    # =====================================

    def evaluar_servicio(
        self,
        cliente_id: int,
        factura_id: int,
        servicio_id: int,
        puntuacion: int,
        comentario: str
    ):

        # =================================
        # VALIDAR PUNTUACIÓN
        # =================================

        if puntuacion < 1 or puntuacion > 5:

            raise HTTPException(
                status_code=400,
                detail=(
                    "La puntuación "
                    "debe ser entre 1 y 5"
                )
            )

        # =================================
        # JUSTIFICACIÓN BAJA
        # =================================

        if puntuacion <= 1 and not comentario:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Debe ingresar "
                    "una justificación"
                )
            )

        # =================================
        # FACTURA
        # =================================

        factura = (
            self.db.query(Factura)
            .filter(
                Factura.id == factura_id,
                Factura.clienteId == cliente_id
            )
            .first()
        )

        if not factura:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Factura no encontrada"
                )
            )

        # =================================
        # VALIDAR PAGADA
        # =================================

        if factura.estadoFactura != EstadoFacturaEnum.PAGADA:

            raise HTTPException(
                status_code=400,
                detail=(
                    "La factura "
                    "no está pagada"
                )
            )

        # =================================
        # VALIDAR MISMO DÍA
        # =================================

        if (
            factura.fechaCreacion.date()
            !=
            nowNaive().date()
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Solo puede evaluar "
                    "servicios el mismo día"
                )
            )

        # =================================
        # VALIDAR COMPRA SERVICIO
        # =================================

        detalle = (
            self.db.query(DetalleFactura)
            .filter(
                DetalleFactura.facturaId == factura_id,
                DetalleFactura.comidaId == servicio_id
            )
            .first()
        )

        if not detalle:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No compró este servicio"
                )
            )

        # =================================
        # EVITAR DUPLICADOS
        # =================================

        existente = (
            self.repository
            .existe_evaluacion_servicio(
                cliente_id,
                factura_id,
                servicio_id
            )
        )

        if existente:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Ya evaluó este servicio"
                )
            )

        # =================================
        # CREAR EVALUACIÓN
        # =================================

        evaluacion = Evaluacion(
            cliente_id=cliente_id,
            factura_id=factura_id,
            servicio_id=servicio_id,
            puntuacion=puntuacion,
            comentario=comentario
        )

        return self.repository.add(
            evaluacion
        )
    

    
    # =========================================================
    # PELÍCULAS EVALUABLES
    # =========================================================

    def obtener_peliculas_evaluables(
        self,
        cliente_id: int,
    ):

        ahora = nowNaive()

        detalles = (
            self.db.query(DetalleFactura)
            .join(Factura)
            .join(Boleta)
            .join(Funcion)
            .filter(
                Factura.clienteId == cliente_id,
                Factura.estadoFactura == EstadoFacturaEnum.PAGADA,
                Funcion.fechaHoraFin < ahora,
            )
            .all()
        )

        resultado = []

        for detalle in detalles:

            boleta = detalle.boleta

            if not boleta:
                continue

            funcion = boleta.funcion

            existe = (
                self.repository
                .existe_evaluacion_pelicula(
                    cliente_id,
                    funcion.id,
                    funcion.peliculaId,
                )
            )

            if existe:
                continue

            resultado.append({

                "funcionId": funcion.id,

                "peliculaId": funcion.peliculaId,

                "titulo": funcion.pelicula.titulo,

                "fechaFuncion": funcion.fechaHora,

            })

        return resultado


    # =========================================================
    # SERVICIOS EVALUABLES
    # =========================================================

    def obtener_servicios_evaluables(
        self,
        cliente_id: int,
    ):

        hoy = nowNaive().date()

        detalles = (
            self.db.query(DetalleFactura)
            .join(Factura)
            .filter(
                Factura.clienteId == cliente_id,
                Factura.estadoFactura == EstadoFacturaEnum.PAGADA,
                cast(Factura.fechaCreacion, Date) == hoy,
                DetalleFactura.comidaId.isnot(None),
            )
            .all()
        )

        resultado = []

        for detalle in detalles:

            existe = (
                self.repository
                .existe_evaluacion_servicio(
                    cliente_id,
                    detalle.facturaId,
                    detalle.comidaId,
                )
            )

            if existe:
                continue

            resultado.append({

                "facturaId": detalle.facturaId,

                "servicioId": detalle.comidaId,

                "nombre": detalle.comida.nombre,

            })

        return resultado


    # =========================================================
    # MIS EVALUACIONES
    # =========================================================

    def obtener_mis_evaluaciones(
        self,
        cliente_id: int,
    ):

        evaluaciones = (
            self.db.query(Evaluacion)
            .filter(
                Evaluacion.cliente_id == cliente_id
            )
            .all()
        )

        resultado = []

        for evaluacion in evaluaciones:

            resultado.append({

                "id": evaluacion.id,

                "puntuacion": evaluacion.puntuacion,

                "comentario": evaluacion.comentario,

                "pelicula": (
                    evaluacion.pelicula.titulo
                    if evaluacion.pelicula
                    else None
                ),

                "servicio": (
                    evaluacion.servicio.nombre
                    if evaluacion.servicio
                    else None
                ),

            })

        return resultado