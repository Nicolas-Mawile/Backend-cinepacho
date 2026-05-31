"""
reporte_seed.py
===============
Enriquece los datos de soporte para los 3 tipos de reportes del sistema.

1. Movilidad de Empleados
   - Actualiza fechaInicio de contratos con fechas históricas para que el
     reporte muestre antigüedad variada por empleado y por multiplex.

2. Ventas Mensuales & Rendimiento por Multiplex
   - Los datos provienen de compra_seed, que distribuye facturas PAGADAS
     a lo largo del mes en curso (mayo 2026) usando funciones de todos
     los multiplex. No se requiere acción adicional aquí.

Requiere: empleados_seed (todos los empleados ya creados).
"""

from datetime import date, timedelta
from sqlalchemy import select

from app.database import SessionLocal
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.contrato import Contrato


# Correo personal del empleado → meses de antigüedad hacia atrás desde hoy
# Diseño: variedad entre 3 y 24 meses para que el reporte sea significativo.
ANTIGUEDADES_EMPLEADOS = {
    # Multiplex 1 – Titán Plaza
    "carlos@gmail.com":        24,   # Director veterano – 2 años
    "lauraramirez@gmail.com":  18,   # Administrador – 1.5 años
    # Multiplex 2 – Unicentro
    "pedro@gmail.com":         12,   # Cajero – 1 año exacto
    "ana@gmail.com":            6,   # Despachador – 6 meses
    # Multiplex 3 – Plaza Central
    "sofia.emp@gmail.com":      9,   # Cajera – 9 meses
    "diego.emp@gmail.com":     15,   # Director – 15 meses
    # Multiplex 4 – Gran Estación
    "valentina.emp@gmail.com": 20,   # Administradora – 20 meses
    "santiago.emp@gmail.com":   4,   # Despachador reciente – 4 meses
    # Multiplex 5 – Embajador
    "camila.emp@gmail.com":     8,   # Cajera – 8 meses
    "andres.emp@gmail.com":     3,   # Aseador más reciente – 3 meses
    # Multiplex 6 – Las Américas
    "isabella.emp@gmail.com":  11,   # Cajera – 11 meses
    "felipe.emp@gmail.com":    14,   # Encargado sala – 14 meses
}


def run():
    with SessionLocal() as db:
        try:
            actualizados = 0

            for correo, meses in ANTIGUEDADES_EMPLEADOS.items():
                empleado = db.execute(
                    select(Empleado).where(Empleado.correo == correo)
                ).scalar_one_or_none()

                if not empleado:
                    continue

                contrato = empleado.contratoActivo
                if not contrato:
                    continue

                nueva_fecha = date.today() - timedelta(days=meses * 30)

                # Solo actualizar si la fecha aún es "hoy" (primer arranque)
                if contrato.fechaInicio >= date.today() - timedelta(days=1):
                    contrato.fechaInicio = nueva_fecha
                    db.flush()
                    actualizados += 1

            db.commit()
            print(f"✅ reporte_seed completado ({actualizados} contratos actualizados)")

        except Exception as e:
            db.rollback()
            raise
