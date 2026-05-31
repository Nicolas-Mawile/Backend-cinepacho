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
from app.utils.timezone import nowColombia, nowNaive
from app.infrastructure.models.recompensaBoleta import RecompensaBoleta

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
        usarRecompensa : bool,
        nombres: str,
        apellidos: str,
        correo: str,
        telefono: str,
    ):
        try:
            print(f"[PAGAR] usarRecompensa={usarRecompensa}")

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

            if factura.fechaExpiracionReserva < nowNaive():

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
            recompensa = None
            boleta_general = None

            if usarRecompensa:
                print(f"[PAGAR] usarRecompensa=True → buscando recompensa para clienteId={cliente.id}")
                recompensa = (
                    self.db.query(RecompensaBoleta)
                    .filter(
                        RecompensaBoleta.clienteId == cliente.id,
                        RecompensaBoleta.utilizada == False,
                        RecompensaBoleta.fechaVencimiento > nowNaive(),
                    )
                    .first()
                )
                print(f"[PAGAR] recompensa encontrada={recompensa}  id={recompensa.id if recompensa else None}")
                if recompensa:
                    for detalle in factura.detalles:

                        if not detalle.boleta:
                            continue

                        if not detalle.boleta.silla:
                            continue

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
                            detail=(
                                "La recompensa solo puede "
                                "aplicarse a boletas GENERAL"
                            ),
                        )

                for detalle in factura.detalles:

                    if not detalle.boleta:
                        continue

                    if not detalle.boleta.silla:
                        continue

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
                        detail=(
                            "La recompensa solo puede "
                            "utilizarse en boletas GENERAL"
                        ),
                    )
            # ─────────────────────────────────────────────────────
            # Calcular monto final
            # ─────────────────────────────────────────────────────

            monto_pago = factura.total

            if recompensa and boleta_general:

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
                recompensaId=(recompensa.id if recompensa else None),
            )

            self.pago_repository.add(pago)

            self.db.flush()

            # ─────────────────────────────────────────────────────
            # Generar token JWT
            # ─────────────────────────────────────────────────────

            token = jwt.encode(
                {
                    "pagoId": pago.id,
                    "exp": nowColombia() + timedelta(minutes=10),
                },
                settings.secret_key,
                algorithm="HS256",
            )

            link_confirmacion = (
                f"{settings.frontend_url}"
                f"/confirmar-pago?token={token}"
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

            print("\n===== ENVIO DE CONFIRMACION =====")
            print(f"[EMAIL] Destinatario : {correo}")
            print(f"[EMAIL] SMTP_USER    : {settings.smtp_user}")
            print(f"[EMAIL] SMTP_SERVER  : {settings.smtp_server}:{settings.smtp_port}")
            print(f"[EMAIL] Link         : {link_confirmacion}")
            print("=================================\n")

            try:
                self.email_service.enviar_confirmacion_pago(
                    destinatario=correo,
                    link_confirmacion=link_confirmacion,
                )
                print(f"[EMAIL] ✓ Correo de confirmación enviado a {correo}")
            except Exception as email_error:
                print(f"[EMAIL] ✗ Falló el envío del correo: {repr(email_error)}")

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

            if pago.fechaExpiracion < nowNaive():
                pago.estado = EstadoPagoEnum.EXPIRADO
                pago.factura.estadoFactura = EstadoFacturaEnum.CANCELADA
                self.db.commit()
                raise HTTPException(status_code=400, detail="La reserva expiró")

            factura = pago.factura
            cliente = factura.cliente

            print(f"[CONFIRMAR] pagoId={pago.id}  recompensaId={pago.recompensaId}  pago.recompensa={pago.recompensa}")
            print(f"[CONFIRMAR] factura.clienteId={factura.clienteId}  factura.cliente={factura.cliente}")
            if factura.cliente:
                print(f"[CONFIRMAR] puntosAcumulados ANTES del reset = {factura.cliente.puntosAcumulados}")

            # ─── Aprobar pago ─────────────────────────────────────
            pago.estado = EstadoPagoEnum.PAGADO
            pago.fechaPago = nowNaive()
            if pago.recompensa:
                pago.recompensa.utilizada = True
                if factura.cliente:
                    factura.cliente.puntosAcumulados = 0
                    print(f"[CONFIRMAR] ✓ Recompensa usada → puntos reseteados a 0")
                else:
                    print(f"[CONFIRMAR] ✗ pago.recompensa existe PERO factura.cliente es None — reset no aplicado")

            # ─── Marcar factura como pagada ───────────────────────
            factura.estadoFactura = EstadoFacturaEnum.PAGADA
            factura.codigoTransaccion = (
                f"TX-{factura.id}-{int(nowColombia().timestamp())}"
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

            if cliente and not pago.recompensa:
                puntos_anteriores = cliente.puntosAcumulados
                cliente.puntosAcumulados = min(100, cliente.puntosAcumulados + puntos_ganados)

                recompensa_activa = (
                    self.db.query(RecompensaBoleta)
                    .filter(
                        RecompensaBoleta.clienteId == cliente.id,
                        RecompensaBoleta.utilizada == False,
                        RecompensaBoleta.fechaVencimiento > nowNaive(),
                    )
                    .first()
                )

                if (
                    puntos_anteriores < 100
                    and cliente.puntosAcumulados == 100
                    and not recompensa_activa
                ):

                    recompensa = RecompensaBoleta(
                        clienteId=cliente.id,
                        fechaOtorgamiento=nowNaive(),
                        fechaVencimiento=(
                            nowNaive()
                            + timedelta(days=180)
                        ),
                        utilizada=False,
                    )

                    self.db.add(recompensa)

            if cliente:
                print(f"[CONFIRMAR] ── PUNTOS FINALES antes del commit ──")
                print(f"[CONFIRMAR]   clienteId={cliente.id}  puntosAcumulados={cliente.puntosAcumulados}")
                print(f"[CONFIRMAR]   recompensa usada={bool(pago.recompensa)}")
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
                    print(f"[EMAIL] Enviando factura #{factura.id} a {correo_destino}")
                    try:
                        self.email_service.enviar_factura_y_boletas(
                            destinatario=correo_destino,
                            factura=factura,
                        )
                        print(f"[EMAIL] ✓ Factura #{factura.id} enviada a {correo_destino}")
                    except Exception as email_error:
                        print(f"[EMAIL] ✗ Falló el envío de factura #{factura.id}: {repr(email_error)}")

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

