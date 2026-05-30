"""Checkout service — reserva de sillas y snacks."""
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app.utils.timezone import nowNaive

from app.config import settings
from app.infrastructure.models.factura import Factura
from app.infrastructure.models.boleta import Boleta
from app.infrastructure.models.detalleFactura import DetalleFactura
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum
from app.infrastructure.models.silla import Silla
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.comida import Comida
from app.domain.services.compra_service import CompraService
from app.infrastructure.repositories.factura_repository import FacturaRepository
from app.infrastructure.repositories.boleta_repository import BoletaRepository
from app.infrastructure.repositories.funcion_repository import FuncionRepository
from app.infrastructure.repositories.silla_repository import SillaRepository
import uuid
from app.infrastructure.models.EstadoPagoEnum import EstadoPagoEnum

class CheckoutService:
    """
    Gestiona el flujo de reserva:
    - checkout (reserva temporal de sillas y/o snacks)
    - cancelación de reservas expiradas
    - disponibilidad de sillas
    """

    def __init__(self, db: Session):
        self.db = db
        self.factura_repository = FacturaRepository(db)
        self.boleta_repository = BoletaRepository(db)
        self.funcion_repository = FuncionRepository(db)
        self.silla_repository = SillaRepository(db)
        self.compra_service = CompraService(db)

    # =========================================================
    # RESERVAS EXPIRADAS
    # =========================================================

    def cancelar_reservas_expiradas(self):
        reservas_expiradas = (
            self.factura_repository.get_expired_reservas()
        )

        canceladas = 0

        for factura in reservas_expiradas:

            # ─────────────────────────────────────────────
            # Cancelar factura
            # ─────────────────────────────────────────────

            factura.estadoFactura = EstadoFacturaEnum.CANCELADA

            # ─────────────────────────────────────────────
            # Expirar pagos pendientes
            # ─────────────────────────────────────────────

            for pago in factura.pagos:

                if pago.estado == EstadoPagoEnum.PENDIENTE:

                    pago.estado = EstadoPagoEnum.EXPIRADO

            canceladas += 1

        self.db.commit()

        print(
            f"[TASK] Reservas expiradas canceladas: {canceladas}"
        )

    # =========================================================
    # CHECKOUT
    # =========================================================

    def checkout(
        self,
        funcion_id: int | None,
        silla_ids: list[int],
        comidas: list,
        permitir_solo_snacks: bool = False,
    ):
        try:
            # Limpiar reservas expiradas antes de procesar
            self.cancelar_reservas_expiradas()
            self.funcion_repository.desactivar_funciones_vencidas()

            tiene_sillas = len(silla_ids) > 0
            tiene_comidas = len(comidas) > 0

            # ─── Validación: debe traer algo ───────────────────────
            if not tiene_sillas and not tiene_comidas:
                raise HTTPException(
                    status_code=400,
                    detail="Debe seleccionar boletas o snacks",
                )

            # ─── Compra solo snacks: solo permitida en punto ágil ──
            if not tiene_sillas and tiene_comidas and not permitir_solo_snacks:
                raise HTTPException(
                    status_code=403,
                    detail="La compra solo de snacks está disponible únicamente en punto ágil",
                )

            # ─── Validaciones de sillas (solo si se pidieron) ──────
            if tiene_sillas:
                if len(set(silla_ids)) != len(silla_ids):
                    raise HTTPException(
                        status_code=400,
                        detail="No puede seleccionar sillas repetidas",
                    )
                if len(silla_ids) > 10:
                    raise HTTPException(
                        status_code=400,
                        detail="Máximo 10 sillas por compra",
                    )

            # ─── Función (obligatoria cuando hay sillas) ───────────
            funcion = None
            if tiene_sillas:
                if not funcion_id:
                    raise HTTPException(
                        status_code=400,
                        detail="Debe indicar la función para comprar boletas",
                    )
                funcion = self.funcion_repository.get_by_id(funcion_id)
                if not funcion:
                    raise HTTPException(status_code=404, detail="Función no encontrada")
                if not funcion.estaActiva:
                    raise HTTPException(status_code=400, detail="La función está inactiva")

                # Cierre de ventas: no se puede comprar después del inicio
                now = nowNaive()
                limite_compra = funcion.fechaHora + timedelta(minutes=20)

                if now > limite_compra:
                    raise HTTPException(status_code=400, detail="La función ya no permite compras",)

            # ─── Crear factura ─────────────────────────────────────
            factura = Factura(
                clienteId=None,
                subTotal=0,
                descuento=0,
                total=0,
                fechaCreacion=nowNaive(),          # ← corregido typo
                fechaExpiracionReserva=nowNaive() + timedelta(minutes=10),
                codigoTransaccion=str(uuid.uuid4()),
                estadoFactura=EstadoFacturaEnum.RESERVADA,
            )
            self.factura_repository.create(factura)

            total_boletas = 0
            subtotal_snacks = 0

            # ─── Procesar sillas ───────────────────────────────────
            if tiene_sillas:
                for silla_id in silla_ids:
                    if self.boleta_repository.existe_boleta_activa(funcion_id, silla_id):
                        raise HTTPException(
                            status_code=400,
                            detail=f"La silla {silla_id} no está disponible",
                        )

                    silla = self.silla_repository.get(silla_id)
                    if not silla:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Silla {silla_id} no encontrada",
                        )
                    if not silla.estaActiva:
                        raise HTTPException(
                            status_code=400,
                            detail=f"La silla {silla_id} está inactiva",
                        )
                    if silla.salaId != funcion.salaId:
                        raise HTTPException(
                            status_code=400,
                            detail=f"La silla {silla_id} no pertenece a la sala de la función",
                        )

                    precio_base = silla.tipoSilla.precio
                    dia_semana = funcion.fechaHora.weekday()
                    # Promoción martes (1) y miércoles (2): mitad de precio
                    if dia_semana in [1, 2]:
                        precio = int(precio_base / 2)
                        print(f"[CHECKOUT] Silla {silla_id} | tipoSilla='{silla.tipoSilla.nombre}' | precio_base={precio_base} | dia_semana={dia_semana} (mar/mie) → precio con 50% dto={precio}")
                    else:
                        precio = precio_base
                        print(f"[CHECKOUT] Silla {silla_id} | tipoSilla='{silla.tipoSilla.nombre}' | precio_base={precio_base} | dia_semana={dia_semana} → sin descuento, precio={precio}")

                    boleta = Boleta(
                        funcionId=funcion_id,
                        sillaId=silla_id,
                    )

                    self.boleta_repository.add(boleta)

                    # IMPORTANTE:
                    # fuerza el INSERT para obtener el ID real
                    self.db.flush()

                    detalle = DetalleFactura(
                        facturaId=factura.id,
                        boletaId=boleta.id,
                        cantidad=1,
                        precioUnitario=precio,
                        subTotal=precio,
                    )

                    self.db.add(detalle)

                    total_boletas += precio

            # ─── Procesar snacks ───────────────────────────────────
            for item in comidas:
                comida = (
                    self.db.query(Comida)
                    .filter(Comida.id == item.comidaId, Comida.estaActiva == True)
                    .first()
                )
                if not comida:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Comida {item.comidaId} no encontrada",
                    )
                if item.cantidad <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Cantidad inválida de snacks",
                    )

                subtotal_item = comida.precio * item.cantidad
                subtotal_snacks += subtotal_item
                detalle_comida = DetalleFactura(
                    facturaId=factura.id,
                    comidaId=comida.id,
                    cantidad=item.cantidad,
                    precioUnitario=comida.precio,
                    subTotal=subtotal_item,
                )
                self.db.add(detalle_comida)

            # ─── Descuento snacks (si aplica promoción) ────────────
            subtotal_snacks_con_descuento = self.compra_service.aplicar_descuento_snacks(
                subtotal_snacks
            )
            descuento_snacks = subtotal_snacks - subtotal_snacks_con_descuento

            # ─── Totales ───────────────────────────────────────────
            subtotal_total = total_boletas + subtotal_snacks
            total_final = total_boletas + subtotal_snacks_con_descuento

            print(f"[CHECKOUT] ── RESUMEN DE TOTALES ──────────────────────")
            print(f"[CHECKOUT]   total_boletas            = {total_boletas}")
            print(f"[CHECKOUT]   subtotal_snacks          = {subtotal_snacks}")
            print(f"[CHECKOUT]   subtotal_snacks_dto      = {subtotal_snacks_con_descuento}")
            print(f"[CHECKOUT]   descuento_snacks         = {descuento_snacks}")
            print(f"[CHECKOUT]   subtotal (sin dto)       = {subtotal_total}")
            print(f"[CHECKOUT]   total_final (a pagar)    = {total_final}")
            print(f"[CHECKOUT] ────────────────────────────────────────────")

            factura.subTotal = subtotal_total
            factura.descuento = descuento_snacks
            factura.total = total_final

            self.db.commit()
            self.db.refresh(factura)

            return {
                "mensaje": "Checkout realizado exitosamente",
                "facturaId": factura.id,
                "estado": factura.estadoFactura,
                "expira": factura.fechaExpiracionReserva,
                "subtotal": factura.subTotal,
                "descuento": factura.descuento,
                "subtotalBoletas": total_boletas,
                "subtotalSnacks": subtotal_snacks,
                "total": factura.total,
            }

        except IntegrityError as e:
            self.db.rollback()

            raise HTTPException(
                status_code=409,
                detail=f"IntegrityError: {str(e.orig)}",
            )
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================
    # DISPONIBILIDAD DE SILLAS
    # =========================================================

    def obtener_disponibilidad(self, funcion_id: int):
        self.funcion_repository.desactivar_funciones_vencidas()
        """Devuelve el estado de cada silla para una función."""
        funcion = self.funcion_repository.get_by_id(funcion_id)
        if not funcion:
            raise HTTPException(status_code=404, detail="Función no encontrada")
        if not funcion.estaActiva:
            raise HTTPException(status_code=400, detail="La función está inactiva")

        sillas = (
            self.db.query(Silla)
            .filter(Silla.salaId == funcion.salaId, Silla.estaActiva.is_(True))
            .all()
        )

        response = []
        now = nowNaive()
        for silla in sillas:
            boleta = (
                self.db.query(Boleta)
                .join(DetalleFactura, DetalleFactura.boletaId == Boleta.id)
                .join(Factura, Factura.id == DetalleFactura.facturaId)
                .filter(
                    Boleta.funcionId == funcion_id,
                    Boleta.sillaId == silla.id,
                    (
                        (Factura.estadoFactura == EstadoFacturaEnum.PAGADA)
                        | (
                            (Factura.estadoFactura == EstadoFacturaEnum.RESERVADA)
                            & (Factura.fechaExpiracionReserva > now)
                        )
                    ),
                )
                .first()
            )

            if boleta:
                factura_boleta = boleta.detalle.factura
                estado = (
                    "OCUPADA"
                    if factura_boleta.estadoFactura == EstadoFacturaEnum.PAGADA
                    else "RESERVADA"
                )
            else:
                estado = "DISPONIBLE"

            response.append(
                {
                    "sillaId": silla.id,
                    "fila": silla.fila,
                    "columna": silla.columna,
                    "tipo": silla.tipoSilla.nombre if silla.tipoSilla else None,
                    "estado": estado,
                }
            )

        return response
