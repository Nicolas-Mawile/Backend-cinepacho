from sqlalchemy.orm import Session

from app.infrastructure.repositories.reporte_repository import (
    ReporteRepository
)

from app.utils.reportes.graficas import (
    GraficasReportes
)

from app.utils.reportes.pdf_generator import (
    PDFGenerator
)


class ReportePdfService:

    def __init__(self, db: Session):

        self.db = db

        self.reporte_repository = (
            ReporteRepository(db)
        )

    # =====================================================
    # REPORTE 1
    # MOVILIDAD EMPLEADOS
    # =====================================================

    def generar_pdf_movilidad(self):
        movilidad = (
            self.reporte_repository
            .obtener_movilidad_empleados()
        )

        salarios = (
            self.reporte_repository
            .obtener_salarios_empleados()
        )

        empleados_por_multiplex = (
            self.reporte_repository
            .obtener_empleados_por_multiplex()
        )

        tabla_resumen = [
            ["Indicador", "Valor"],
            [
                "Total empleados",
                movilidad["totalEmpleados"],
            ],
            [
                "Salario mínimo",
                f"${movilidad['salarioMinimo']:,.0f}",
            ],
            [
                "Salario promedio",
                f"${movilidad['salarioPromedio']:,.0f}",
            ],
            [
                "Salario máximo",
                f"${movilidad['salarioMaximo']:,.0f}",
            ],
            [
                "Antigüedad promedio (meses)",
                movilidad["antiguedadPromedioMeses"],
            ],
        ]

        grafica_empleados = (
            GraficasReportes
            .crear_grafica_barras(
                labels=[
                    item["multiplex"]
                    for item in empleados_por_multiplex
                ],
                valores=[
                    item["cantidad"]
                    for item in empleados_por_multiplex
                ],
                titulo="Empleados por Multiplex",
                xlabel="Multiplex",
                ylabel="Cantidad de empleados",
            )
        )

        grafica_salarios = (
            GraficasReportes
            .crear_histograma(
                valores=salarios,
                titulo="Distribución Salarial",
                xlabel="Salario",
            )
        )

        return PDFGenerator.generar_pdf(
            titulo="Reporte de Movilidad de Empleados",
            subtitulo="Gestión de Talento Humano",
            descripcion=(
                "El presente informe consolida la información "
                "estadística relacionada con la planta de personal "
                "de CinePacho. Se presentan indicadores de salarios, "
                "antigüedad y distribución de empleados por multiplex."
            ),
            indicadores=[
                (
                    "Empleados",
                    movilidad["totalEmpleados"]
                ),
                (
                    "Salario Prom.",
                    f"${movilidad['salarioPromedio']:,.0f}"
                ),
                (
                    "Salario Máx.",
                    f"${movilidad['salarioMaximo']:,.0f}"
                ),
                (
                    "Antigüedad",
                    f"{movilidad['antiguedadPromedioMeses']} meses"
                ),
            ],
            tablas=[
                tabla_resumen
            ],
            imagenes=[
                grafica_empleados,
                grafica_salarios,
            ],
        )

    # =====================================================
    # REPORTE 2
    # OPERACIONAL MENSUAL
    # =====================================================

    def generar_pdf_operacional(
    self,
    mes: int,
    anio: int,
):

        ventas = (
            self.reporte_repository
            .obtener_ventas_mensuales(
                mes,
                anio,
            )
        )

        ventas_por_multiplex = (
            self.reporte_repository
            .obtener_ventas_por_multiplex(
                mes,
                anio,
            )
        )

        tabla_resumen = [
            ["Indicador", "Valor"],
            [
                "Facturas pagadas",
                ventas["facturasPagadas"],
            ],
            [
                "Ingresos totales",
                f"${ventas['ingresosTotales']:,.0f}",
            ],
            [
                "Boletas vendidas",
                ventas["boletasVendidas"],
            ],
            [
                "Productos vendidos",
                ventas["productosVendidos"],
            ],
        ]

        grafica_distribucion = (
            GraficasReportes
            .crear_grafica_pie(
                labels=[
                    "Boletas",
                    "Productos",
                ],
                valores=[
                    ventas["boletasVendidas"],
                    ventas["productosVendidos"],
                ],
                titulo="Distribución de Ventas",
            )
        )

        grafica_ingresos = (
            GraficasReportes
            .crear_grafica_barras(
                labels=[
                    item["multiplex"]
                    for item in ventas_por_multiplex
                ],
                valores=[
                    item["ventas"]
                    for item in ventas_por_multiplex
                ],
                titulo="Ingresos por Multiplex",
                xlabel="Multiplex",
                ylabel="Ingresos",
            )
        )

        return PDFGenerator.generar_pdf(
            titulo=f"Reporte Operacional {mes}/{anio}",
            subtitulo="Indicadores Comerciales",
            descripcion=(
                "Este informe presenta los principales "
                "indicadores operativos y comerciales "
                "registrados durante el periodo seleccionado. "
                "La información corresponde a ventas, "
                "facturación y comercialización de productos."
            ),
            indicadores=[
                (
                    "Ingresos",
                    f"${ventas['ingresosTotales']:,.0f}"
                ),
                (
                    "Facturas",
                    ventas["facturasPagadas"]
                ),
                (
                    "Boletas",
                    ventas["boletasVendidas"]
                ),
                (
                    "Productos",
                    ventas["productosVendidos"]
                ),
            ],
            tablas=[
                tabla_resumen
            ],
            imagenes=[
                grafica_distribucion,
                grafica_ingresos,
            ],
        )
    # =====================================================
    # REPORTE 3
    # DESEMPEÑO MULTIPLEX
    # =====================================================

    def generar_pdf_desempeno_multiplex(
    self,
    mes: int,
    anio: int,
):

        rendimiento = (
            self.reporte_repository
            .obtener_rendimiento_multiplex(
                mes,
                anio,
            )
        )

        tabla_rendimiento = [
            [
                "Multiplex",
                "Ventas",
                "Boletas Vendidas",
            ]
        ]

        for item in rendimiento:

            tabla_rendimiento.append(
                [
                    item["multiplex"],
                    f"${item['ventas']:,.0f}",
                    item["boletasVendidas"],
                ]
            )

        ventas_totales = sum(
            item["ventas"]
            for item in rendimiento
        )

        boletas_totales = sum(
            item["boletasVendidas"]
            for item in rendimiento
        )

        cantidad_multiplex = len(
            rendimiento
        )

        grafica_ranking = (
            GraficasReportes
            .crear_grafica_barras(
                labels=[
                    item["multiplex"]
                    for item in rendimiento
                ],
                valores=[
                    item["ventas"]
                    for item in rendimiento
                ],
                titulo="Ranking de Multiplex",
                xlabel="Multiplex",
                ylabel="Ventas",
            )
        )

        grafica_participacion = (
            GraficasReportes
            .crear_grafica_pie(
                labels=[
                    item["multiplex"]
                    for item in rendimiento
                ],
                valores=[
                    item["ventas"]
                    for item in rendimiento
                ],
                titulo="Participación por Multiplex",
            )
        )

        return PDFGenerator.generar_pdf(
            titulo="Reporte de Desempeño de Multiplex",
            subtitulo=f"Periodo {mes}/{anio}",
            descripcion=(
                "El presente informe consolida el desempeño "
                "comercial de los multiplex registrados "
                "durante el periodo analizado. Se incluyen "
                "indicadores de ventas, volumen de boletas "
                "y participación relativa de cada sede."
            ),
            indicadores=[
                (
                    "Multiplex",
                    cantidad_multiplex
                ),
                (
                    "Ventas Tot.",
                    f"${ventas_totales:,.0f}"
                ),
                (
                    "Boletas",
                    boletas_totales
                ),
                (
                    "Periodo",
                    f"{mes}/{anio}"
                ),
            ],
            tablas=[
                tabla_rendimiento
            ],
            imagenes=[
                grafica_ranking,
                grafica_participacion,
            ],
        )