"""Checkout service."""
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.config import settings
from jose import jwt
from app.infrastructure.models.factura import Factura
from app.infrastructure.models.boleta import Boleta
from app.infrastructure.models.detalleFactura import DetalleFactura
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum
from app.infrastructure.models.silla import Silla
from app.infrastructure.models.pago import Pago
from app.infrastructure.models.EstadoPagoEnum import EstadoPagoEnum
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.repositories.pago_repository import (PagoRepository)
from app.domain.services.email_service import (EmailService)
from app.infrastructure.repositories.factura_repository import (FacturaRepository)
from app.infrastructure.repositories.boleta_repository import (BoletaRepository)
from app.infrastructure.repositories.funcion_repository import (FuncionRepository)
from app.infrastructure.repositories.silla_repository import (SillaRepository)

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
        self.pago_repository = PagoRepository(db)

        self.email_service = EmailService()

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
                    .existe_boleta_activa(
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

                self.boleta_repository.add(
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

    def pagar(self, factura_id: int, metodo_pago: str, correo: str, cliente_id: int | None = None):

        try:

            # =====================================
            # FACTURA
            # =====================================

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
            # VALIDAR ESTADO
            # =====================================

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

            # =====================================
            # VALIDAR EXPIRACIÓN
            # =====================================

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

            # =====================================
            # VALIDAR PROPIETARIO
            # SOLO SI HAY CLIENTE LOGIN
            # =====================================

            if (
                cliente_id is not None
                and
                factura.clienteId is not None
                and
                factura.clienteId != cliente_id
            ):

                raise HTTPException(
                    status_code=403,
                    detail=(
                        "No puede pagar "
                        "esta factura"
                    )
                )

            # =====================================
            # CREAR PAGO PENDIENTE
            # =====================================

            pago = Pago(
                monto=factura.total,
                estado=EstadoPagoEnum.PENDIENTE,
                metodoPago=metodo_pago,
                fechaPago=None,
                fechaExpiracion=(
                    factura.fechaExpiracionReserva
                ),
                facturaId=factura.id
            )

            self.pago_repository.add(
                pago
            )

            # =====================================
            # GENERAR TOKEN JWT
            # =====================================

            token = jwt.encode(
                {
                    "pagoId": pago.id,
                    "exp": (
                        datetime.utcnow()
                        + timedelta(minutes=10)
                    )
                },
                settings.secret_key,
                algorithm="HS256"
            )

            # =====================================
            # LINK CONFIRMACIÓN
            # =====================================

            link_confirmacion = (
                f"{settings.backend_url}"
                f"/confirmar-pago"
                f"?token={token}"
            )
            print("\n========== LINK CONFIRMACIÓN ==========")
            print(link_confirmacion)
            print("=======================================\n")

            # =====================================
            # ENVIAR EMAIL
            # =====================================

            self.email_service.enviar_confirmacion_pago(
                destinatario=correo,
                link_confirmacion=link_confirmacion
            )

            self.db.commit()

            return {
                "mensaje": (
                    "Correo de confirmación "
                    "enviado"
                ),
                "facturaId": factura.id,
                "pagoId": pago.id,
                "estadoPago": pago.estado,
                "expira": pago.fechaExpiracion
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
                .joinedload(Funcion.pelicula),

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.funcion)
                .joinedload(Funcion.sala)

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
                        f"Sala {boleta.funcion.sala.numero}"
                    ),

                    "fechaHora": (
                        boleta.funcion
                        .fechaHora
                    ),

                    "sillaId": boleta.silla.id,

                    "fila": str(boleta.silla.fila),
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
                .joinedload(Funcion.pelicula),

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.funcion)
                .joinedload(Funcion.sala)

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
                        f"Sala {boleta.funcion.sala.numero}"
                    ),

                    "fechaHora": (
                        boleta.funcion
                        .fechaHora
                    ),

                    "sillaId": boleta.silla.id,

                    "fila": str(boleta.silla.fila),
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
                .joinedload(Funcion.pelicula),

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.funcion)
                .joinedload(Funcion.sala)

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
                            f"Sala {boleta.funcion.sala.numero}"
                        ),

                        "fechaHora": (
                            boleta.funcion
                            .fechaHora
                        ),

                        "sillaId": boleta.silla.id,

                        "fila": str(boleta.silla.fila),
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
    

    def confirmar_pago(
    self,
    token: str,
    nombres: str,
    apellidos: str,
    correo: str,
    telefono: str
):

        try:

            # =====================================
            # DECODIFICAR TOKEN
            # =====================================

            try:

                payload = jwt.decode(
                    token,
                    settings.secret_key,
                    algorithms=["HS256"]
                )

            except jwt.ExpiredSignatureError:

                raise HTTPException(
                    status_code=400,
                    detail="El enlace expiró"
                )

            except jwt.InvalidTokenError:

                raise HTTPException(
                    status_code=400,
                    detail="Token inválido"
                )

            pago_id = payload.get("pagoId")

            if not pago_id:

                raise HTTPException(
                    status_code=400,
                    detail="Token inválido"
                )

            # =====================================
            # BUSCAR PAGO
            # =====================================

            pago = (
                self.pago_repository
                .get(pago_id)
            )

            if not pago:

                raise HTTPException(
                    status_code=404,
                    detail="Pago no encontrado"
                )

            # =====================================
            # VALIDAR ESTADO
            # =====================================

            if (
                pago.estado
                != EstadoPagoEnum.PENDIENTE
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "El pago ya fue procesado"
                    )
                )

            # =====================================
            # VALIDAR EXPIRACIÓN
            # =====================================

            if (
                pago.fechaExpiracion
                < datetime.utcnow()
            ):

                pago.estado = (
                    EstadoPagoEnum.EXPIRADO
                )

                pago.factura.estadoFactura = (
                    EstadoFacturaEnum.CANCELADA
                )

                self.db.commit()

                raise HTTPException(
                    status_code=400,
                    detail="La reserva expiró"
                )

            factura = pago.factura

            # =====================================
            # BUSCAR CLIENTE EXISTENTE
            # =====================================

            cliente = (
                self.db.query(Cliente)
                .filter(
                    Cliente.correo == correo
                )
                .first()
            )

            # =====================================
            # CREAR CLIENTE INVITADO
            # =====================================

            if not cliente:

                cliente = Cliente(
                    nombres=nombres,
                    apellidos=apellidos,
                    correo=correo,
                    telefono=telefono,
                    puntosAcumulados=0,
                    estaActivo=True
                )

                self.db.add(cliente)

                self.db.flush()

            # =====================================
            # ASOCIAR CLIENTE
            # =====================================

            factura.clienteId = cliente.id

            # =====================================
            # APROBAR PAGO
            # =====================================

            pago.estado = (
                EstadoPagoEnum.APROBADO
            )

            pago.fechaPago = datetime.utcnow()

            # =====================================
            # PAGAR FACTURA
            # =====================================

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
                    "Pago confirmado "
                    "correctamente"
                ),
                "facturaId": factura.id,
                "codigoTransaccion": (
                    factura.codigoTransaccion
                ),
                "estadoFactura": (
                    factura.estadoFactura
                ),
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