"""Servicio de compras y promociones."""

from datetime import datetime
from app.infrastructure.repositories.configuracion_repository import ConfiguracionRepository
from sqlalchemy.orm import Session


class CompraService:
    """Gestiona compras, promociones y descuentos."""
    
    def __init__(self, db: Session):
        self.config_repo = ConfiguracionRepository(db)
    
    def aplicar_descuento_snacks(self, monto_snacks: float) -> float:
        """Aplica descuento en snacks si está activo hoy."""
        # Verificar si promoción está activa
        promo_activa = self.config_repo.get_por_clave("promo_snack_activa")
        if not promo_activa or promo_activa.valor.lower() != "true":
            return monto_snacks
        
        # Verificar si es día de promoción
        dia_actual = datetime.now().weekday()  # 0=lunes, 6=domingo
        
        dias_config = self.config_repo.get_por_clave("promo_snack_dias")
        if not dias_config:
            return monto_snacks
        
        dias_promo = [int(d.strip()) for d in dias_config.valor.split(",")]
        
        if dia_actual not in dias_promo:
            return monto_snacks
        
        # Aplicar descuento
        porcentaje = self.config_repo.get_por_clave("promo_snack_porcentaje")
        descuento = int(porcentaje.valor) if porcentaje else 50
        
        return monto_snacks * (1 - descuento / 100)
    
    def validar_cantidad_boletas(self, cantidad: int) -> bool:
        """Valida que no exceda máximo por transacción."""
        config = self.config_repo.get_por_clave("max_boletas_transaccion")
        max_boletas = int(config.valor) if config else 10
        return cantidad <= max_boletas
