from pydantic import BaseModel
from typing import List


class EmpleadosPorMultiplexResponse(BaseModel):
    multiplex: str
    cantidad: int


class ReporteMovilidadResponse(BaseModel):
    totalEmpleados: int

    salarioMinimo: float
    salarioPromedio: float
    salarioMaximo: float

    antiguedadPromedioMeses: float

    empleadosPorMultiplex: List[
        EmpleadosPorMultiplexResponse
    ]


class ReporteVentasMensualesResponse(BaseModel):
    mes: int
    anio: int

    facturasPagadas: int

    ingresosTotales: float

    boletasVendidas: int
    productosVendidos: int


class RendimientoMultiplexResponse(BaseModel):
    multiplex: str

    ventas: float

    boletasVendidas: int