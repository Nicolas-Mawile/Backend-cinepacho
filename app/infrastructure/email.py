"""Email infrastructure for sending notifications."""

import smtplib
import logging
from email.message import EmailMessage
from app.config import settings

logger = logging.getLogger(__name__)

def enviar_bienvenida(nombre: str, correo: str):
    """
    Envía un correo electrónico de bienvenida a un nuevo cliente.
    Se espera que esta función se ejecute de forma asíncrona (e.g., via asyncio.create_task).
    """
    if not all([settings.smtp_server, settings.smtp_port, settings.smtp_user, settings.smtp_password]):
        logger.warning("Configuración SMTP incompleta. No se enviará el correo de bienvenida.")
        return

    msg = EmailMessage()
    msg['Subject'] = f"¡Bienvenido a Cine Pacho, {nombre}!"
    msg['From'] = settings.smtp_user
    msg['To'] = correo

    # Template HTML con logo textual y link
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .container {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
            }}
            .header {{
                text-align: center;
                color: #e50914;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            .content {{
                line-height: 1.6;
                color: #333;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 12px;
                color: #777;
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #e50914;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                CINE PACHO
            </div>
            <div class="content">
                <p>Hola <strong>{nombre}</strong>,</p>
                <p>¡Gracias por unirte a Cine Pacho! Estamos emocionados de tenerte con nosotros.</p>
                <p>Ya puedes empezar a disfrutar de la mejor cartelera y acumular puntos en cada visita.</p>
                <center>
                    <a href="{settings.frontend_url}" class="button" style="color: white;">Ir a la aplicación</a>
                </center>
            </div>
            <div class="footer">
                &copy; 2026 Cine Pacho. Todos los derechos reservados.
            </div>
        </div>
    </body>
    </html>
    """
    msg.set_content(f"Hola {nombre}, ¡bienvenido a Cine Pacho! Visítanos en {settings.frontend_url}")
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()  # TLS seguro
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
            logger.info(f"Correo de bienvenida enviado exitosamente a {correo}")
    except Exception as e:
        logger.error(f"Error al enviar correo de bienvenida a {correo}: {str(e)}")
