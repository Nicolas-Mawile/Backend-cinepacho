from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.infrastructure.models.factura import Factura
from app.infrastructure.models.boleta import Boleta
from app.infrastructure.models.detalleFactura import DetalleFactura
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum
from app.infrastructure.models.pago import Pago
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.models.EstadoPagoEnum import EstadoPagoEnum
from app.infrastructure.repositories.pago_repository import PagoRepository
from app.infrastructure.repositories.factura_repository import FacturaRepository
from app.domain.services.email_service import EmailService


class PagoService:
    """
    Gestiona el flujo de pago:
    - Solicitar pago (genera token y envía email)
    - Confirmar pago (via link del correo)
    """

    def __init__(self, db: Session):
        self.db = db
        self.factura_repository = FacturaRepository(db)
        self.pago_repository = PagoRepository(db)
        self.email_service = EmailService()

    # =========================================================
    # SOLICITAR PAGO
    # =========================================================

    def pagar(
        self,
        factura_id: int,
        metodo_pago: str,

        nombres: str,
        apellidos: str,
        correo: str,
        telefono: str,
    ):
        try:

            factura = self.factura_repository.get_by_id(factura_id)

            if not factura:
                raise HTTPException(
                    status_code=404,
                    detail="Factura no encontrada",
                )

            # ─────────────────────────────────────────────────────
            # Validar estado factura
            # ─────────────────────────────────────────────────────

            if factura.estadoFactura != EstadoFacturaEnum.RESERVADA:
                raise HTTPException(
                    status_code=400,
                    detail="La factura no está en estado RESERVADA",
                )

            # ─────────────────────────────────────────────────────
            # Validar expiración
            # ─────────────────────────────────────────────────────

            if factura.fechaExpiracionReserva < datetime.utcnow():

                factura.estadoFactura = EstadoFacturaEnum.CANCELADA

                self.db.commit()

                raise HTTPException(
                    status_code=400,
                    detail="La reserva expiró",
                )

            # ─────────────────────────────────────────────────────
            # Buscar o crear cliente
            # ─────────────────────────────────────────────────────

            cliente = (
                self.db.query(Cliente)
                .filter(Cliente.correo == correo)
                .first()
            )

            if not cliente:

                cliente = Cliente(
                    nombres=nombres,
                    apellidos=apellidos,
                    correo=correo,
                    telefono=telefono,
                )

                self.db.add(cliente)

                self.db.flush()

            # Asociar cliente a factura
            factura.clienteId = cliente.id

            # ─────────────────────────────────────────────────────
            # Validar pago con puntos
            # ─────────────────────────────────────────────────────

            usar_puntos = metodo_pago.lower() == "puntos"

            boleta_general = None

            if usar_puntos:

                if cliente.puntosAcumulados < 100:
                    raise HTTPException(
                        status_code=400,
                        detail="No tiene suficientes puntos (necesita 100)",
                    )

                # Buscar boleta GENERAL
                for detalle in factura.detalles:

                    if detalle.boleta and detalle.boleta.silla:

                        tipo_silla = detalle.boleta.silla.tipoSilla

                        if (
                            tipo_silla
                            and tipo_silla.nombre.lower() == "general"
                        ):
                            boleta_general = detalle
                            break

                if not boleta_general:
                    raise HTTPException(
                        status_code=400,
                        detail="No hay boletas GENERAL para redimir puntos",
                    )

            # ─────────────────────────────────────────────────────
            # Calcular monto final
            # ─────────────────────────────────────────────────────

            monto_pago = factura.total

            if usar_puntos and boleta_general:

                monto_pago = max(
                    0.0,
                    monto_pago - boleta_general.subTotal,
                )

            # ─────────────────────────────────────────────────────
            # Crear pago pendiente
            # ─────────────────────────────────────────────────────

            pago = Pago(
                monto=monto_pago,
                estado=EstadoPagoEnum.PENDIENTE,
                metodoPago=metodo_pago,
                fechaPago=None,
                fechaExpiracion=factura.fechaExpiracionReserva,
                facturaId=factura.id,
            )

            self.pago_repository.add(pago)

            self.db.flush()

            # ─────────────────────────────────────────────────────
            # Generar token JWT
            # ─────────────────────────────────────────────────────

            token = jwt.encode(
                {
                    "pagoId": pago.id,
                    "exp": datetime.utcnow() + timedelta(minutes=10),
                },
                settings.secret_key,
                algorithm="HS256",
            )

            link_confirmacion = (
                f"{settings.backend_url}"
                f"/api/v1/compras/confirmar-pago?token={token}"
            )

            # ─────────────────────────────────────────────────────
            # Debug consola
            # ─────────────────────────────────────────────────────

            print("\n========== LINK CONFIRMACIÓN ==========")
            print(link_confirmacion)
            print("=======================================\n")

            # ─────────────────────────────────────────────────────
            # Enviar email
            # ─────────────────────────────────────────────────────

            # try:
            print("\n===== ENVIO DE CONFIRMACION =====")
            print("Correo recibido:", correo)
            print("Link:", link_confirmacion)
            print("SMTP_USER:", settings.smtp_user)
            print("=================================\n")

            self.email_service.enviar_confirmacion_pago(
                destinatario=correo,
                link_confirmacion=link_confirmacion,
            )

            # except Exception as email_error:

            #     print(
            #         f"[ADVERTENCIA] "
            #         f"No se pudo enviar el email: {email_error}"
            #     )

            # ─────────────────────────────────────────────────────
            # Commit final
            # ─────────────────────────────────────────────────────

            self.db.commit()

            return {
                "mensaje": "Correo de confirmación enviado",
                "facturaId": factura.id,
                "pagoId": pago.id,
                "estadoPago": pago.estado,
                "expira": pago.fechaExpiracion,
            }

        except HTTPException:

            self.db.rollback()

            raise

        except Exception as e:

            self.db.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e),
            )

    # =========================================================
    # CONFIRMAR PAGO (desde el link del correo)
    # =========================================================

    def confirmar_pago(self, token: str):
        try:
            # ─── Decodificar token ────────────────────────────────
            try:
                payload = jwt.decode(
                    token, settings.secret_key, algorithms=["HS256"]
                )
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=400, detail="El enlace de confirmación expiró")
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=400, detail="Token inválido")

            pago_id = payload.get("pagoId")
            if not pago_id:
                raise HTTPException(status_code=400, detail="Token inválido")

            # ─── Buscar pago ──────────────────────────────────────
            pago = self.pago_repository.get(pago_id)
            if not pago:
                raise HTTPException(status_code=404, detail="Pago no encontrado")

            if pago.estado != EstadoPagoEnum.PENDIENTE:
                raise HTTPException(
                    status_code=400,
                    detail="El pago ya fue procesado",
                )

            if pago.fechaExpiracion < datetime.utcnow():
                pago.estado = EstadoPagoEnum.EXPIRADO
                pago.factura.estadoFactura = EstadoFacturaEnum.CANCELADA
                self.db.commit()
                raise HTTPException(status_code=400, detail="La reserva expiró")

            factura = pago.factura
            cliente = factura.cliente

            # ─── Aprobar pago ─────────────────────────────────────
            pago.estado = EstadoPagoEnum.PAGADO
            pago.fechaPago = datetime.utcnow()     # ← corregido (era utcnow())

            # ─── Marcar factura como pagada ───────────────────────
            factura.estadoFactura = EstadoFacturaEnum.PAGADA
            factura.codigoTransaccion = (
                f"TX-{factura.id}-{int(datetime.utcnow().timestamp())}"
            )

            # ─── Fidelización ─────────────────────────────────────
            # La spec dice: 10 pts por boletas, 5 pts por snacks (independientes)
            tiene_boletas = any(d.boletaId is not None for d in factura.detalles)
            tiene_snacks = any(d.comidaId is not None for d in factura.detalles)

            puntos_ganados = 0
            if tiene_boletas:
                puntos_ganados += 10
            if tiene_snacks:
                puntos_ganados += 5

            if cliente:
                # Si se pagó con puntos, descontar 100 primero
                if pago.metodoPago.lower() == "puntos":
                    cliente.puntosAcumulados = max(0, cliente.puntosAcumulados - 100)

                # Acumular puntos ganados en esta compra
                cliente.puntosAcumulados += puntos_ganados
                # ← SIN min(): los puntos pueden seguir acumulándose

            self.db.commit()
            self.db.refresh(factura)

            # ─── Enviar email con boletas y factura ───────────────
            if cliente:
                correo_destino = (
                    cliente.correo
                    if hasattr(cliente, "correo")
                    else None
                )
                if correo_destino:
                    try:
                        self.email_service.enviar_factura_y_boletas(
                            destinatario=correo_destino,
                            factura=factura,
                        )
                    except Exception as email_error:
                        print(f"[ADVERTENCIA] No se pudo enviar la factura: {email_error}")

            return {
                "mensaje": "Pago confirmado correctamente",
                "facturaId": factura.id,
                "codigoTransaccion": factura.codigoTransaccion,
                "estadoFactura": factura.estadoFactura,
                "total": factura.total,
            }

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

