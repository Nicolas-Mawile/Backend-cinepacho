import smtplib

from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart

from app.config import settings


class EmailService:

    """
    Servicio de envío de correos.
    """

    def enviar_confirmacion_pago(
        self,
        destinatario: str,
        link_confirmacion: str
    ):

        asunto = (
            "Confirmación de pago - CinePacho"
        )

        cuerpo = f"""
Hola.

Tu compra está casi lista.

Para confirmar el pago, haz clic en el siguiente enlace:

{link_confirmacion}

IMPORTANTE:
Este enlace expirará en 10 minutos.

CinePacho
"""

        mensaje = MIMEMultipart()

        mensaje["From"] = settings.smtp_user

        mensaje["To"] = destinatario

        mensaje["Subject"] = asunto

        mensaje.attach(
            MIMEText(cuerpo, "plain")
        )

        servidor = smtplib.SMTP(
            settings.smtp_server,
            settings.smtp_port
        )

        servidor.starttls()

        servidor.login(
            settings.smtp_user,
            settings.smtp_password
        )

        servidor.send_message(mensaje)

        servidor.quit()