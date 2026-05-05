"""Unit tests for email infrastructure."""

import pytest
from unittest.mock import MagicMock, patch
from app.infrastructure.email import enviar_bienvenida
from app.config import settings

@patch("smtplib.SMTP")
def test_enviar_bienvenida_llamada_correcta(mock_smtp):
    """Verifica que se llame a SMTP con los parámetros correctos."""
    # Configurar settings para el test
    with patch.object(settings, "smtp_server", "smtp.test.com"), \
         patch.object(settings, "smtp_port", 587), \
         patch.object(settings, "smtp_user", "test@cinepacho.com"), \
         patch.object(settings, "smtp_password", "password123"):
        
        # Mock de la instancia del servidor
        instance = mock_smtp.return_value.__enter__.return_value
        
        enviar_bienvenida("Juan Perez", "juan@example.com")
        
        # Verificar conexión
        mock_smtp.assert_called_with("smtp.test.com", 587)
        
        # Verificar TLS y Login
        instance.starttls.assert_called_once()
        instance.login.assert_called_with("test@cinepacho.com", "password123")
        
        # Verificar que se envió un mensaje
        assert instance.send_message.called
        msg = instance.send_message.call_args[0][0]
        assert msg['To'] == "juan@example.com"
        assert "Juan Perez" in msg['Subject']

@patch("smtplib.SMTP")
def test_enviar_bienvenida_falla_no_bloquea(mock_smtp):
    """Verifica que un fallo en SMTP no lance excepción hacia arriba (solo loguea)."""
    with patch.object(settings, "smtp_server", "smtp.test.com"), \
         patch.object(settings, "smtp_port", 587), \
         patch.object(settings, "smtp_user", "test@cinepacho.com"), \
         patch.object(settings, "smtp_password", "password123"):
        
        # Configurar el mock para que falle
        mock_smtp.side_effect = Exception("SMTP Connection Error")
        
        # No debería lanzar excepción
        try:
            enviar_bienvenida("Juan Perez", "juan@example.com")
        except Exception as e:
            pytest.fail(f"enviar_bienvenida lanzó una excepción inesperada: {e}")

@patch("app.infrastructure.email.logger")
def test_enviar_bienvenida_config_incompleta(mock_logger):
    """Verifica que si la config está incompleta se loguee un warning."""
    with patch.object(settings, "smtp_server", None):
        enviar_bienvenida("Juan", "test@test.com")
        mock_logger.warning.assert_called_with("Configuración SMTP incompleta. No se enviará el correo de bienvenida.")
