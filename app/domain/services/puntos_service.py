"""Servicio de cálculo de puntos y lealtad."""

from app.infrastructure.repositories.configuracion_repository import ConfiguracionRepository
from sqlalchemy.orm import Session


class PuntosService:
    """Calcula y gestiona puntos de lealtad."""
    
    def __init__(self, db: Session):
        self.config_repo = ConfiguracionRepository(db)
    
    def calcular_puntos_boleta(self, cantidad_boletas: int) -> int:
        """Calcula puntos por compra de boletas usando config dinámica."""
        config = self.config_repo.get_por_clave("puntos_por_boleta")
        puntos_unitarios = int(config.valor) if config else 10
        return cantidad_boletas * puntos_unitarios
    
    def calcular_puntos_snack(self, monto: float) -> int:
        """Calcula puntos por compra de snacks."""
        config = self.config_repo.get_por_clave("puntos_por_snack")
        puntos_unitarios = int(config.valor) if config else 5
        # Ejemplo: 1 punto por cada 10 pesos gastados
        return int(monto / 10) * puntos_unitarios
    
    def puntos_necesarios_para_regalo(self) -> int:
        """Obtiene puntos requeridos para boleta regalo."""
        config = self.config_repo.get_por_clave("puntos_para_regalo")
        return int(config.valor) if config else 100
