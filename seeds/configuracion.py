"""Seed data for configuración del sistema."""

from sqlalchemy import select

from app.infrastructure.models.configuracion import Configuracion
from app.database import SessionLocal


CONFIG_DATA = [
    ("timer_reserva_minutos", "10", "Minutos para completar pago después de reserva", "int"),
    ("cierre_venta_minutos", "20", "Minutos post-inicio de función para cerrar venta", "int"),
    ("max_boletas_transaccion", "10", "Máximo de boletas por transacción", "int"),
    
    ("puntos_por_boleta", "10", "Puntos acumulados por cada boleta comprada", "int"),
    ("puntos_por_snack", "5", "Puntos acumulados por compra de snacks", "int"),
    ("puntos_para_regalo", "100", "Puntos necesarios para boleta regalo", "int"),
    ("meses_vigencia_boleta_regalo", "6", "Meses de vigencia de la boleta regalo", "int"),
    
    ("promo_snack_activa", "false", "Si la promoción de snacks está activa", "bool"),
]


def run():
    """
    Carga configuración del sistema.
    Idempotente: solo inserta si no existen registros.
    """
    with SessionLocal() as db:
        try:
            # Verificar si ya existen registros
            stmt = select(Configuracion).limit(1)
            result = db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                return
            
            # Insertar nuevos datos
            for clave, valor, descripcion, tipo in CONFIG_DATA:
                config = Configuracion(
                    clave=clave,
                    valor=valor,
                    descripcion=descripcion,
                    tipo=tipo,
                    activo=True
                )
                db.add(config)
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise


if __name__ == "__main__":
    """Ejecutar directamente: python seeds/configuracion.py"""
    run()