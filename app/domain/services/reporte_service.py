from sqlalchemy.orm import Session

from app.infrastructure.repositories.reporte_repository import (
    ReporteRepository
)


class ReporteService:

    def __init__(self, db: Session):

        self.db = db

        self.reporte_repository = (
            ReporteRepository(db)
        )

    # =====================================================
    # MOVILIDAD EMPLEADOS
    # =====================================================

    def obtener_movilidad_empleados(self):

        return (
            self.reporte_repository
            .obtener_movilidad_empleados()
        )

    # =====================================================
    # VENTAS MENSUALES
    # =====================================================

    def obtener_ventas_mensuales(
        self,
        mes: int,
        anio: int,
    ):

        if mes < 1 or mes > 12:

            raise ValueError(
                "El mes debe estar entre 1 y 12"
            )

        if anio < 2000:

            raise ValueError(
                "Año inválido"
            )

        return (
            self.reporte_repository
            .obtener_ventas_mensuales(
                mes=mes,
                anio=anio,
            )
        )

    # =====================================================
    # RENDIMIENTO MULTIPLEX
    # =====================================================

    def obtener_rendimiento_multiplex(
        self,
        mes: int,
        anio: int,
    ):

        if mes < 1 or mes > 12:

            raise ValueError(
                "El mes debe estar entre 1 y 12"
            )

        if anio < 2000:

            raise ValueError(
                "Año inválido"
            )

        return (
            self.reporte_repository
            .obtener_rendimiento_multiplex(
                mes=mes,
                anio=anio,
            )
        )