"""Seed data for configuración del sistema."""

import asyncio
from sqlalchemy import select

from app.models.configuracion import Configuracion
from app.database import AsyncSessionLocal


CONFIG_DATA = [
    ("timer_reserva_minutos", "10", "Minutos para completar pago después de reserva", "int"),
    ("cierre_venta_minutos", "20", "Minutos post-inicio de función para cerrar venta", "int"),
    ("max_boletas_transaccion", "10", "Máximo de boletas por transacción", "int"),
    
    ("puntos_por_boleta", "10", "Puntos acumulados por cada boleta comprada", "int"),
    ("puntos_por_snack", "5", "Puntos acumulados por compra de snacks", "int"),
    ("puntos_para_regalo", "100", "Puntos necesarios para boleta regalo", "int"),
    ("meses_vigencia_boleta_regalo", "6", "Meses de vigencia de la boleta regalo", "int"),
    
    ("promo_snack_activa", "true", "Si la promoción de snacks está activa", "bool"),
    ("promo_snack_porcentaje", "50", "Porcentaje de descuento en snacks con promo", "int"),
    ("promo_snack_dias", "1,2", "Días de promo: 0=lunes, 1=martes, ..., 6=domingo", "str"),
]


async def run():
    """
    Carga configuración del sistema.
    Idempotente: solo inserta si no existen registros.
    """
    async with AsyncSessionLocal() as db:
        try:
            # Verificar si ya existen registros
            stmt = select(Configuracion).limit(1)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                print("✓ Seed configuracion: ya existen registros, omitiendo.")
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
            
            await db.commit()
            print(f"✓ Seed configuracion: {len(CONFIG_DATA)} valores insertados.")
            
        except Exception as e:
            await db.rollback()
            print(f"✗ Error en seed configuracion: {str(e)}")
            raise


if __name__ == "__main__":
    """Ejecutar directamente: python seeds/configuracion.py"""
    asyncio.run(run())