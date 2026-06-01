"""Email infrastructure for sending notifications."""
import logging
import resend
from app.config import settings

logger = logging.getLogger(__name__)


def enviar_bienvenida(nombre: str, correo: str):
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY no configurada — no se envía correo de bienvenida.")
        return

    resend.api_key = settings.resend_api_key

    html_content = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;border:1px solid #ddd;border-radius:8px;">
        <div style="text-align:center;color:#e50914;font-size:24px;font-weight:bold;margin-bottom:20px;">CINE PACHO</div>
        <div style="line-height:1.6;color:#333;">
            <p>Hola <strong>{nombre}</strong>,</p>
            <p>¡Gracias por unirte a Cine Pacho! Estamos emocionados de tenerte con nosotros.</p>
            <p>Ya puedes empezar a disfrutar de la mejor cartelera y acumular puntos en cada visita.</p>
            <center>
                <a href="{settings.frontend_url}" style="display:inline-block;padding:10px 20px;background-color:#e50914;color:white;text-decoration:none;border-radius:5px;margin-top:20px;">
                    Ir a la aplicación
                </a>
            </center>
        </div>
        <div style="margin-top:30px;text-align:center;font-size:12px;color:#777;">&copy; 2026 Cine Pacho. Todos los derechos reservados.</div>
    </div>
    """

    try:
        resend.Emails.send({
            "from": settings.email_from,
            "to": [correo],
            "subject": f"¡Bienvenido a Cine Pacho, {nombre}!",
            "html": html_content,
            "text": f"Hola {nombre}, ¡bienvenido a Cine Pacho! Visítanos en {settings.frontend_url}",
        })
        logger.info("Correo de bienvenida enviado a %s", correo)
    except Exception as e:
        logger.error("Error al enviar correo de bienvenida a %s: %s", correo, repr(e))
