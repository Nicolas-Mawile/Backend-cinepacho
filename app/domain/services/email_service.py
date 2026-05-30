"""Email service — notificaciones de CinePacho."""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Envío de correos transaccionales."""

    def _smtp_disponible(self) -> bool:
        return all([
            settings.smtp_server,
            settings.smtp_port,
            settings.smtp_user,
            settings.smtp_password,
        ])

    def _enviar(self, mensaje, destinatario):

        try:

            print("===== ENVIANDO EMAIL =====")
            print("TO:", destinatario)

            servidor = smtplib.SMTP(
                settings.smtp_server,
                settings.smtp_port
            )

            servidor.set_debuglevel(1)

            servidor.starttls()

            servidor.login(
                settings.smtp_user,
                settings.smtp_password
            )

            servidor.send_message(mensaje)

            servidor.quit()

            print("EMAIL ENVIADO")

        except Exception as e:

            print("ERROR SMTP:", repr(e))
            raise

    # =========================================================
    # CONFIRMACIÓN DE PAGO (link)
    # =========================================================

    def enviar_confirmacion_pago(self, destinatario: str, link_confirmacion: str):
        asunto = "Confirma tu pago — CinePacho"
        cuerpo = f"""\
Hola,

Tu compra está casi lista. Para confirmar el pago haz clic en el enlace:

{link_confirmacion}

IMPORTANTE: Este enlace expira en 10 minutos.
Si no realizaste esta compra, ignora este correo.

CinePacho
"""
        msg = MIMEMultipart()
        msg["From"] = settings.smtp_user or "no-reply@cinepacho.com"
        msg["To"] = destinatario
        msg["Subject"] = asunto
        msg.attach(MIMEText(cuerpo, "plain"))
        self._enviar(msg, destinatario)

    # =========================================================
    # RESET DE CONTRASEÑA (link)
    # =========================================================

    def enviar_reset_password(self, destinatario: str, link_reset: str):
        asunto = "Restablece tu contraseña — CinePacho"
        cuerpo = f"""\
Hola,

Recibimos una solicitud para restablecer la contraseña de tu cuenta.
Para crear una nueva contraseña haz clic en el enlace:

{link_reset}

IMPORTANTE: Este enlace expira en 15 minutos.
Si no solicitaste el cambio de contraseña, ignora este correo.

CinePacho
"""
        msg = MIMEMultipart()
        msg["From"] = settings.smtp_user or "no-reply@cinepacho.com"
        msg["To"] = destinatario
        msg["Subject"] = asunto
        msg.attach(MIMEText(cuerpo, "plain"))
        self._enviar(msg, destinatario)

    # =========================================================
    # FACTURA Y BOLETAS (tras confirmar pago)
    # =========================================================

    def enviar_factura_y_boletas(self, destinatario: str, factura):
        """
        Envía al cliente su factura y las boletas compradas.
        `factura` es la instancia ORM de Factura con detalles cargados.
        """
        asunto = f"Tu compra #{factura.id} está confirmada — CinePacho"

        # Construir tabla de boletas
        lineas_boletas = []
        lineas_snacks = []
        for detalle in factura.detalles:
            if detalle.boleta:
                b = detalle.boleta
                lineas_boletas.append(
                    f"  • {b.funcion.pelicula.titulo} | "
                    f"Sala {b.funcion.sala.numero} | "
                    f"{b.funcion.fechaHora.strftime('%d/%m/%Y %H:%M')} | "
                    f"Fila {b.silla.fila} Col {b.silla.columna}"
                )
            if detalle.comida:
                lineas_snacks.append(
                    f"  • {detalle.comida.nombre} x{detalle.cantidad} = ${detalle.subTotal:,.0f}"
                )

        seccion_boletas = (
            "BOLETAS:\n" + "\n".join(lineas_boletas)
            if lineas_boletas
            else ""
        )
        seccion_snacks = (
            "SNACKS:\n" + "\n".join(lineas_snacks)
            if lineas_snacks
            else ""
        )

        cuerpo = f"""\
¡Tu compra está confirmada!

Código de transacción: {factura.codigoTransaccion}
Total pagado: ${factura.total:,.0f}

{seccion_boletas}

{seccion_snacks}

Gracias por elegir CinePacho.
"""
        msg = MIMEMultipart()
        msg["From"] = settings.smtp_user or "no-reply@cinepacho.com"
        msg["To"] = destinatario
        msg["Subject"] = asunto
        msg.attach(MIMEText(cuerpo, "plain"))
        self._enviar(msg, destinatario)
        logger.info("Factura enviada a %s (factura #%s)", destinatario, factura.id)

    # =========================================================
    # NOTIFICACIÓN DE PUNTOS (100 pts acumulados)
    # =========================================================

    def enviar_notificacion_puntos(self, destinatario: str, puntos: int):
        asunto = "¡Tienes puntos para una boleta gratis! — CinePacho"
        cuerpo = f"""\
¡Felicitaciones!

Has acumulado {puntos} puntos en CinePacho.

Tienes derecho a una boleta general GRATIS válida por 6 meses.
Para usarla, selecciona "Pagar con puntos" en tu próxima compra.

CinePacho
"""
        msg = MIMEMultipart()
        msg["From"] = settings.smtp_user or "no-reply@cinepacho.com"
        msg["To"] = destinatario
        msg["Subject"] = asunto
        msg.attach(MIMEText(cuerpo, "plain"))
        self._enviar(msg, destinatario)
