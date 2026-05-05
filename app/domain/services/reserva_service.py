"""Servicio de reservas y temporizadores."""

from app.infrastructure.repositories.configuracion_repository import ConfiguracionRepository
from sqlalchemy.orm import Session


class ReservaService:
    """Gestiona reservas con timer dinámico."""
    
    def __init__(self, db: Session):
        self.config_repo = ConfiguracionRepository(db)
    
    def obtener_timer_reserva(self) -> int:
        """Retorna minutos para completar reserva."""
        config = self.config_repo.get_por_clave("timer_reserva_minutos")
        return int(config.valor) if config else 10
    
    def obtener_cierre_venta(self) -> int:
        """Retorna minutos post-inicio para cerrar venta."""
        config = self.config_repo.get_por_clave("cierre_venta_minutos")
        return int(config.valor) if config else 20