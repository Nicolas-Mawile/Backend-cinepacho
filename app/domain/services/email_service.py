"""Email service — notificaciones de CinePacho via Resend."""
import logging
import resend
from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:

    def _enviar(self, to: str, subject: str, html: str, text: str):
        if not settings.resend_api_key:
            print("ERROR: RESEND_API_KEY no configurada — no se envía correo")
            return

        resend.api_key = settings.resend_api_key

        try:
            print(f"[EMAIL] Enviando a {to} — {subject}")
            resend.Emails.send({
                "from": settings.email_from,
                "to": [to],
                "subject": subject,
                "html": html,
                "text": text,
            })
            print(f"[EMAIL] OK — correo enviado a {to}")
        except Exception as e:
            print(f"[EMAIL] ERROR Resend: {repr(e)}")
            raise

    # =========================================================
    # CONFIRMACIÓN DE PAGO
    # =========================================================

    def enviar_confirmacion_pago(self, destinatario: str, link_confirmacion: str):
        subject = "Confirma tu pago — CinePacho"
        text = f"""\
Hola,

Tu compra está casi lista. Para confirmar el pago haz clic en el enlace:

{link_confirmacion}

IMPORTANTE: Este enlace expira en 10 minutos.
Si no realizaste esta compra, ignora este correo.

CinePacho
"""
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;border:1px solid #ddd;border-radius:8px;">
            <div style="text-align:center;color:#e50914;font-size:24px;font-weight:bold;margin-bottom:20px;">CINE PACHO</div>
            <p>Tu compra está casi lista. Para confirmar el pago haz clic aquí:</p>
            <center>
                <a href="{link_confirmacion}" style="display:inline-block;padding:10px 20px;background-color:#e50914;color:white;text-decoration:none;border-radius:5px;margin-top:20px;">
                    Confirmar pago
                </a>
            </center>
            <p style="margin-top:20px;color:#777;font-size:13px;">
                IMPORTANTE: Este enlace expira en 10 minutos.<br>
                Si no realizaste esta compra, ignora este correo.
            </p>
            <div style="margin-top:30px;text-align:center;font-size:12px;color:#777;">&copy; 2026 Cine Pacho. Todos los derechos reservados.</div>
        </div>
        """
        self._enviar(destinatario, subject, html, text)

    # =========================================================
    # RESET DE CONTRASEÑA
    # =========================================================

    def enviar_reset_password(self, destinatario: str, link_reset: str):
        subject = "Restablece tu contraseña — CinePacho"
        text = f"""\
Hola,

Recibimos una solicitud para restablecer la contraseña de tu cuenta.
Para crear una nueva contraseña haz clic en el enlace:

{link_reset}

IMPORTANTE: Este enlace expira en 15 minutos.
Si no solicitaste el cambio de contraseña, ignora este correo.

CinePacho
"""
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;border:1px solid #ddd;border-radius:8px;">
            <div style="text-align:center;color:#e50914;font-size:24px;font-weight:bold;margin-bottom:20px;">CINE PACHO</div>
            <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta.</p>
            <center>
                <a href="{link_reset}" style="display:inline-block;padding:10px 20px;background-color:#e50914;color:white;text-decoration:none;border-radius:5px;margin-top:20px;">
                    Restablecer contraseña
                </a>
            </center>
            <p style="margin-top:20px;color:#777;font-size:13px;">
                IMPORTANTE: Este enlace expira en 15 minutos.<br>
                Si no solicitaste el cambio de contraseña, ignora este correo.
            </p>
            <div style="margin-top:30px;text-align:center;font-size:12px;color:#777;">&copy; 2026 Cine Pacho. Todos los derechos reservados.</div>
        </div>
        """
        self._enviar(destinatario, subject, html, text)

    # =========================================================
    # FACTURA Y BOLETAS
    # =========================================================

    def enviar_factura_y_boletas(self, destinatario: str, factura):
        subject = f"Tu compra #{factura.id} está confirmada — CinePacho"

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

        seccion_boletas = "BOLETAS:\n" + "\n".join(lineas_boletas) if lineas_boletas else ""
        seccion_snacks = "SNACKS:\n" + "\n".join(lineas_snacks) if lineas_snacks else ""

        text = f"""\
¡Tu compra está confirmada!

Código de transacción: {factura.codigoTransaccion}
Total pagado: ${factura.total:,.0f}

{seccion_boletas}

{seccion_snacks}

Gracias por elegir CinePacho.
"""
        html_boletas = "".join(f"<li>{l.strip()}</li>" for l in lineas_boletas)
        html_snacks = "".join(f"<li>{l.strip()}</li>" for l in lineas_snacks)
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;border:1px solid #ddd;border-radius:8px;">
            <div style="text-align:center;color:#e50914;font-size:24px;font-weight:bold;margin-bottom:20px;">CINE PACHO</div>
            <h2 style="color:#333;">¡Tu compra está confirmada!</h2>
            <p><strong>Código de transacción:</strong> {factura.codigoTransaccion}</p>
            <p><strong>Total pagado:</strong> ${factura.total:,.0f}</p>
            {"<h3>Boletas</h3><ul>" + html_boletas + "</ul>" if html_boletas else ""}
            {"<h3>Snacks</h3><ul>" + html_snacks + "</ul>" if html_snacks else ""}
            <p>Gracias por elegir CinePacho.</p>
            <div style="margin-top:30px;text-align:center;font-size:12px;color:#777;">&copy; 2026 Cine Pacho. Todos los derechos reservados.</div>
        </div>
        """
        self._enviar(destinatario, subject, html, text)
        logger.info("Factura enviada a %s (factura #%s)", destinatario, factura.id)

    # =========================================================
    # NOTIFICACIÓN DE PUNTOS
    # =========================================================

    def enviar_notificacion_puntos(self, destinatario: str, puntos: int):
        subject = "¡Tienes puntos para una boleta gratis! — CinePacho"
        text = f"""\
¡Felicitaciones!

Has acumulado {puntos} puntos en CinePacho.

Tienes derecho a una boleta general GRATIS válida por 6 meses.
Para usarla, selecciona "Pagar con puntos" en tu próxima compra.

CinePacho
"""
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;border:1px solid #ddd;border-radius:8px;">
            <div style="text-align:center;color:#e50914;font-size:24px;font-weight:bold;margin-bottom:20px;">CINE PACHO</div>
            <h2>¡Felicitaciones!</h2>
            <p>Has acumulado <strong>{puntos} puntos</strong> en CinePacho.</p>
            <p>Tienes derecho a una boleta general <strong>GRATIS</strong> válida por 6 meses.</p>
            <p>Para usarla, selecciona <em>"Pagar con puntos"</em> en tu próxima compra.</p>
            <div style="margin-top:30px;text-align:center;font-size:12px;color:#777;">&copy; 2026 Cine Pacho. Todos los derechos reservados.</div>
        </div>
        """
        self._enviar(destinatario, subject, html, text)
