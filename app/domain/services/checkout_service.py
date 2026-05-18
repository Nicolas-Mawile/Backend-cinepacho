"""Checkout service."""

from datetime import datetime, timedelta

from fastapi import HTTPException

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.infrastructure.models.factura import Factura
from app.infrastructure.models.boleta import Boleta
from app.infrastructure.models.detalleFactura import DetalleFactura
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum
from app.infrastructure.models.silla import Silla

from app.infrastructure.repositories.factura_repository import (
    FacturaRepository
)

from app.infrastructure.repositories.boleta_repository import (
    BoletaRepository
)

from app.infrastructure.repositories.funcion_repository import (
    FuncionRepository
)

from app.infrastructure.repositories.silla_repository import (
    SillaRepository
)


class CheckoutService:
    """
    Servicio encargado del flujo de compra:
    - checkout
    - bloqueo temporal
    - pago
    - confirmación
    """

    def __init__(
        self,
        db: Session
    ):

        self.db = db

        self.factura_repository = (
            FacturaRepository(db)
        )

        self.boleta_repository = (
            BoletaRepository(db)
        )

        self.funcion_repository = (
            FuncionRepository(db)
        )

        self.silla_repository = (
            SillaRepository(db)
        )

    # =========================================================
    # RESERVAS EXPIRADAS
    # =========================================================

    def cancelar_reservas_expiradas(self):
        """
        Libera reservas expiradas automáticamente.
        """

        reservas_expiradas = (
            self.factura_repository
            .get_expired_reservas()
        )

        for factura in reservas_expiradas:

            factura.estadoFactura = (
                EstadoFacturaEnum.CANCELADA
            )

        self.db.commit()

    # =========================================================
    # CHECKOUT
    # =========================================================

    def checkout(
        self,
        cliente_id: int,
        funcion_id: int,
        silla_ids: list[int]
    ):

        try:

            # =====================================
            # LIBERAR EXPIRADAS
            # =====================================

            self.cancelar_reservas_expiradas()

            # =====================================
            # VALIDACIONES
            # =====================================

            if len(silla_ids) == 0:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Debe seleccionar "
                        "al menos una silla"
                    )
                )

            # =====================================
            # VALIDAR DUPLICADOS
            # =====================================

            if len(set(silla_ids)) != len(silla_ids):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "No puede seleccionar "
                        "sillas repetidas"
                    )
                )

            if len(silla_ids) > 10:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Máximo 10 sillas "
                        "por compra"
                    )
                )

            # =====================================
            # FUNCIÓN
            # =====================================

            funcion = (
                self.funcion_repository
                .get_by_id(funcion_id)
            )

            if not funcion:

                raise HTTPException(
                    status_code=404,
                    detail="Función no encontrada"
                )

            if not funcion.estaActiva:

                raise HTTPException(
                    status_code=400,
                    detail="La función está inactiva"
                )

            # =====================================
            # VALIDAR CIERRE VENTAS
            # =====================================

            limite_venta = (
                funcion.fechaHora
                + timedelta(minutes=20)
            )

            if datetime.utcnow() > limite_venta:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "La función ya "
                        "cerró ventas"
                    )
                )

            # =====================================
            # CREAR FACTURA
            # =====================================

            factura = Factura(
                clienteId=cliente_id,
                subTotal=0,
                descuento=0,
                total=0,
                fechaCreacion=datetime.utcnow(),
                fechaExpiracionReserva=(
                    datetime.utcnow()
                    + timedelta(minutes=10)
                ),
                codigoTransaccion="PENDIENTE",
                estadoFactura=(
                    EstadoFacturaEnum.RESERVADA
                )
            )

            self.factura_repository.create(
                factura
            )

            total = 0

            # =====================================
            # PROCESAR SILLAS
            # =====================================

            for silla_id in silla_ids:

                ocupada = (
                    self.boleta_repository
                    .silla_ocupada_o_reservada(
                        funcion_id,
                        silla_id
                    )
                )

                if ocupada:

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"La silla "
                            f"{silla_id} "
                            f"no está disponible"
                        )
                    )

                silla = (
                    self.silla_repository
                    .get(silla_id)
                )

                if not silla:

                    raise HTTPException(
                        status_code=404,
                        detail=(
                            f"Silla "
                            f"{silla_id} "
                            f"no encontrada"
                        )
                    )

                # =====================================
                # VALIDAR SILLA ACTIVA
                # =====================================

                if not silla.estaActiva:

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"La silla "
                            f"{silla_id} "
                            f"está inactiva"
                        )
                    )

                # =====================================
                # VALIDAR SALA
                # =====================================

                if silla.salaId != funcion.salaId:

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"La silla "
                            f"{silla_id} "
                            f"no pertenece "
                            f"a la sala "
                            f"de la función"
                        )
                    )

                precio = (
                    silla.tipoSilla.precio
                )

                boleta = Boleta(
                    funcionId=funcion_id,
                    sillaId=silla_id
                )

                self.boleta_repository.create(
                    boleta
                )

                detalle = DetalleFactura(
                    facturaId=factura.id,
                    boletaId=boleta.id,
                    cantidad=1,
                    precioUnitario=precio,
                    subTotal=precio
                )

                self.db.add(detalle)

                total += precio

            factura.subTotal = total
            factura.total = total

            self.db.commit()

            self.db.refresh(factura)

            return {
                "mensaje": (
                    "Checkout realizado "
                    "exitosamente"
                ),
                "facturaId": factura.id,
                "estado": factura.estadoFactura,
                "expira": (
                    factura
                    .fechaExpiracionReserva
                ),
                "subtotal": factura.subTotal,
                "total": factura.total
            }

        except IntegrityError:

            self.db.rollback()

            raise HTTPException(
                status_code=409,
                detail=(
                    "Una o más sillas "
                    "ya fueron tomadas"
                )
            )

        except HTTPException:

            self.db.rollback()

            raise

        except Exception as e:

            self.db.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    # =========================================================
    # PAGAR
    # =========================================================

    def pagar(
        self,
        factura_id: int,
        cliente_id: int
    ):

        try:

            factura = (
                self.factura_repository
                .get_by_id(factura_id)
            )

            if not factura:

                raise HTTPException(
                    status_code=404,
                    detail="Factura no encontrada"
                )

            # =====================================
            # VALIDAR PROPIETARIO
            # =====================================

            if factura.clienteId != cliente_id:

                raise HTTPException(
                    status_code=403,
                    detail=(
                        "No puede pagar "
                        "esta factura"
                    )
                )

            if (
                factura.estadoFactura
                != EstadoFacturaEnum.RESERVADA
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "La factura "
                        "no está reservada"
                    )
                )

            if (
                factura.fechaExpiracionReserva
                < datetime.utcnow()
            ):

                factura.estadoFactura = (
                    EstadoFacturaEnum.CANCELADA
                )

                self.db.commit()

                raise HTTPException(
                    status_code=400,
                    detail="La reserva expiró"
                )

            factura.estadoFactura = (
                EstadoFacturaEnum.PAGADA
            )

            factura.codigoTransaccion = (
                f"TX-{factura.id}-"
                f"{int(datetime.utcnow().timestamp())}"
            )

            self.db.commit()

            self.db.refresh(factura)

            return {
                "mensaje": (
                    "Compra realizada "
                    "exitosamente"
                ),
                "facturaId": factura.id,
                "codigoTransaccion": (
                    factura.codigoTransaccion
                ),
                "estado": factura.estadoFactura,
                "total": factura.total
            }

        except HTTPException:

            self.db.rollback()

            raise

        except Exception as e:

            self.db.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
    # =========================================================
    # RESUMEN
    # =========================================================

    def obtener_resumen(
        self,
        factura_id: int,
        cliente_id: int
    ):

        factura = (
            self.db.query(Factura)
            .options(

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.silla),

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.funcion)
                .joinedload("pelicula"),

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.funcion)
                .joinedload("sala")

            )
            .filter(Factura.id == factura_id)
            .first()
        )

        if not factura:

            raise HTTPException(
                status_code=404,
                detail="Factura no encontrada"
            )

        if factura.clienteId != cliente_id:

            raise HTTPException(
                status_code=403,
                detail=(
                    "No puede acceder "
                    "a esta factura"
                )
            )

        detalles = []

        for detalle in factura.detalles:

            if detalle.boleta:

                boleta = detalle.boleta

                detalles.append({
                    "boletaId": boleta.id,

                    "funcionId": boleta.funcion.id,

                    "pelicula": (
                        boleta.funcion
                        .pelicula.titulo
                    ),

                    "sala": (
                        boleta.funcion
                        .sala.nombre
                    ),

                    "fechaHora": (
                        boleta.funcion
                        .fechaHora
                    ),

                    "sillaId": boleta.silla.id,

                    "fila": boleta.silla.fila,
                    "columna": boleta.silla.columna,

                    "subtotal": detalle.subTotal
                })

        return {
            "facturaId": factura.id,
            "estado": factura.estadoFactura,

            "subtotal": factura.subTotal,
            "descuento": factura.descuento,
            "total": factura.total,

            "expira": (
                factura.fechaExpiracionReserva
            ),

            "detalles": detalles
        }
    # =========================================================
    # CONFIRMACIÓN
    # =========================================================

    def obtener_confirmacion(
        self,
        factura_id: int,
        cliente_id: int
    ):

        factura = (
            self.db.query(Factura)
            .options(

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.silla),

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.funcion)
                .joinedload("pelicula"),

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.funcion)
                .joinedload("sala")

            )
            .filter(Factura.id == factura_id)
            .first()
        )

        if not factura:

            raise HTTPException(
                status_code=404,
                detail="Factura no encontrada"
            )

        if factura.clienteId != cliente_id:

            raise HTTPException(
                status_code=403,
                detail=(
                    "No puede acceder "
                    "a esta factura"
                )
            )

        if (
            factura.estadoFactura
            != EstadoFacturaEnum.PAGADA
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "La factura aún "
                    "no ha sido pagada"
                )
            )

        boletas = []

        for detalle in factura.detalles:

            if detalle.boleta:

                boleta = detalle.boleta

                boletas.append({
                    "boletaId": boleta.id,

                    "funcionId": boleta.funcion.id,

                    "pelicula": (
                        boleta.funcion
                        .pelicula.titulo
                    ),

                    "sala": (
                        boleta.funcion
                        .sala.nombre
                    ),

                    "fechaHora": (
                        boleta.funcion
                        .fechaHora
                    ),

                    "sillaId": boleta.silla.id,

                    "fila": boleta.silla.fila,
                    "columna": boleta.silla.columna
                })

        return {
            "factura": {
                "id": factura.id,
                "total": factura.total,
                "estado": factura.estadoFactura,
                "codigoTransaccion": (
                    factura.codigoTransaccion
                ),
                "fecha": factura.fechaCreacion
            },
            "boletas": boletas
        }

    # =========================================================
    # MIS BOLETAS
    # =========================================================

    def obtener_mis_boletas(
        self,
        cliente_id: int
    ):

        facturas = (
            self.db.query(Factura)
            .options(

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.silla),

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.funcion)
                .joinedload("pelicula"),

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.funcion)
                .joinedload("sala")

            )
            .filter(
                Factura.clienteId == cliente_id,
                Factura.estadoFactura
                == EstadoFacturaEnum.PAGADA
            )
            .all()
        )

        boletas = []

        for factura in facturas:

            for detalle in factura.detalles:

                if detalle.boleta:

                    boleta = detalle.boleta

                    boletas.append({
                        "boletaId": boleta.id,
                        "facturaId": factura.id,

                        "funcionId": boleta.funcion.id,

                        "pelicula": (
                            boleta.funcion
                            .pelicula.titulo
                        ),

                        "sala": (
                            boleta.funcion
                            .sala.nombre
                        ),

                        "fechaHora": (
                            boleta.funcion
                            .fechaHora
                        ),

                        "sillaId": boleta.silla.id,

                        "fila": boleta.silla.fila,
                        "columna": boleta.silla.columna,

                        "fechaCompra": (
                            factura.fechaCreacion
                        )
                    })

        return boletas
        # =========================================================
    # DISPONIBILIDAD
    # =========================================================

    def obtener_disponibilidad(
        self,
        funcion_id: int
    ):
        """
        Obtiene disponibilidad de sillas
        para una función.
        """

        funcion = (
            self.funcion_repository
            .get_by_id(funcion_id)
        )

        if not funcion:

            raise HTTPException(
                status_code=404,
                detail="Función no encontrada"
            )

        if not funcion.estaActiva:

            raise HTTPException(
                status_code=400,
                detail="La función está inactiva"
            )

        sillas = (
            self.db.query(Silla)
            .filter(
                Silla.salaId == funcion.salaId,
                Silla.estaActiva.is_(True)
            )
            .all()
        )

        response = []

        for silla in sillas:

            boleta = (
                self.db.query(Boleta)
                .join(
                    DetalleFactura,
                    DetalleFactura.boletaId == Boleta.id
                )
                .join(
                    Factura,
                    Factura.id == DetalleFactura.facturaId
                )
                .filter(
                    Boleta.funcionId == funcion_id,
                    Boleta.sillaId == silla.id,
                    (
                        (
                            Factura.estadoFactura
                            == EstadoFacturaEnum.PAGADA
                        )
                        |
                        (
                            (
                                Factura.estadoFactura
                                == EstadoFacturaEnum.RESERVADA
                            )
                            &
                            (
                                Factura
                                .fechaExpiracionReserva
                                > datetime.utcnow()
                            )
                        )
                    )
                )
                .first()
            )

            estado = "DISPONIBLE"

            if boleta:

                factura = boleta.detalle.factura

                if (
                    factura.estadoFactura
                    == EstadoFacturaEnum.PAGADA
                ):
                    estado = "OCUPADA"

                else:
                    estado = "RESERVADA"

            response.append({
                "sillaId": silla.id,
                "fila": silla.fila,
                "columna": silla.columna,
                "estado": estado
            })

        return response