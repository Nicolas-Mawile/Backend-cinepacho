"""Email infrastructure for sending notifications."""
import logging
import requests
from app.config import settings

logger = logging.getLogger(__name__)

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def enviar_bienvenida(nombre: str, correo: str):
    if not settings.brevo_api_key:
        logger.warning("BREVO_API_KEY no configurada — no se envía correo de bienvenida.")
        return

    html_content = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;border:1px solid #ddd;border-radius:8px;">
        <div style="text-align:center;color:#e50914;font-size:24px;font-weight:bold;margin-bottom:20px;">CINE PACHO</div>
        <div style="line-height:1.6;color:#333;">
            <p>Hola <strong>{nombre}</strong>,</p>
            <p>¡Gracias por unirte a Cine Pacho! Estamos emocionados de tenerte con nosotros.</p>
            <p>Ya puedes empezar a disfrutar de la mejor cartelera y acumular puntos en cada visita.</p>
            <p style="word-break:break-all;background:#f5f5f5;padding:12px;border-radius:4px;font-size:13px;">{settings.frontend_url}</p>
        </div>
        <div style="margin-top:30px;text-align:center;font-size:12px;color:#777;">&copy; 2026 Cine Pacho. Todos los derechos reservados.</div>
    </div>
    """

    try:
        response = requests.post(
            BREVO_URL,
            headers={
                "api-key": settings.brevo_api_key,
                "content-type": "application/json",
            },
            json={
                "sender": {"name": "Cine Pacho", "email": settings.email_from},
                "to": [{"email": correo}],
                "subject": f"¡Bienvenido a Cine Pacho, {nombre}!",
                "htmlContent": html_content,
                "textContent": f"Hola {nombre}, ¡bienvenido a Cine Pacho! Visítanos en {settings.frontend_url}",
                "trackClicks": False,
                "trackOpens": False,
            },
            timeout=15,
        )
        response.raise_for_status()
        logger.info("Correo de bienvenida enviado a %s", correo)
    except Exception as e:
        logger.error("Error al enviar correo de bienvenida a %s: %s", correo, repr(e))
