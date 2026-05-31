from datetime import date

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.infrastructure.models.contrato import Contrato
from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.models.factura import Factura
from app.infrastructure.models.detalleFactura import DetalleFactura
from app.infrastructure.models.boleta import Boleta
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.sala import Sala
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum


class ReporteRepository:

    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # REPORTE DE MOVILIDAD DE EMPLEADOS
    # =====================================================

    def obtener_movilidad_empleados(self):

        contratos_activos = (
            self.db.query(Contrato)
            .filter(Contrato.activo.is_(True))
        )

        total_empleados = contratos_activos.count()

        salario_promedio = (
            contratos_activos.with_entities(
                func.avg(Contrato.salario)
            ).scalar()
            or 0
        )

        salario_minimo = (
            contratos_activos.with_entities(
                func.min(Contrato.salario)
            ).scalar()
            or 0
        )

        salario_maximo = (
            contratos_activos.with_entities(
                func.max(Contrato.salario)
            ).scalar()
            or 0
        )

        contratos = contratos_activos.all()

        antiguedades = []

        for contrato in contratos:

            dias = (
                date.today()
                - contrato.fechaInicio
            ).days

            antiguedades.append(
                dias / 30
            )

        antiguedad_promedio = (
            sum(antiguedades) / len(antiguedades)
            if antiguedades
            else 0
        )

        empleados_por_multiplex = (
            self.db.query(
                Multiplex.nombre,
                func.count(Contrato.id)
            )
            .join(
                Contrato,
                Contrato.multiplexId == Multiplex.id
            )
            .filter(
                Contrato.activo.is_(True)
            )
            .group_by(
                Multiplex.nombre
            )
            .order_by(
                func.count(Contrato.id).desc()
            )
            .all()
        )

        return {
            "totalEmpleados": total_empleados,
            "salarioMinimo": float(salario_minimo),
            "salarioPromedio": float(salario_promedio),
            "salarioMaximo": float(salario_maximo),
            "antiguedadPromedioMeses": round(
                antiguedad_promedio,
                2
            ),
            "empleadosPorMultiplex": [
                {
                    "multiplex": nombre,
                    "cantidad": cantidad,
                }
                for nombre, cantidad in empleados_por_multiplex
            ],
        }

    # =====================================================
    # REPORTE DE VENTAS MENSUALES
    # =====================================================

    def obtener_ventas_mensuales(
        self,
        mes: int,
        anio: int,
    ):

        facturas_pagadas = (
            self.db.query(Factura)
            .filter(
                Factura.estadoFactura
                == EstadoFacturaEnum.PAGADA
            )
            .filter(
                extract(
                    "month",
                    Factura.fechaCreacion
                )
                == mes
            )
            .filter(
                extract(
                    "year",
                    Factura.fechaCreacion
                )
                == anio
            )
        )

        cantidad_facturas = (
            facturas_pagadas.count()
        )

        ingresos_totales = (
            facturas_pagadas.with_entities(
                func.sum(Factura.total)
            ).scalar()
            or 0
        )

        boletas_vendidas = (
            self.db.query(
                func.count(
                    DetalleFactura.id
                )
            )
            .join(
                Factura,
                Factura.id
                == DetalleFactura.facturaId
            )
            .filter(
                Factura.estadoFactura
                == EstadoFacturaEnum.PAGADA
            )
            .filter(
                extract(
                    "month",
                    Factura.fechaCreacion
                )
                == mes
            )
            .filter(
                extract(
                    "year",
                    Factura.fechaCreacion
                )
                == anio
            )
            .filter(
                DetalleFactura.boletaId.isnot(
                    None
                )
            )
            .scalar()
            or 0
        )

        productos_vendidos = (
            self.db.query(
                func.sum(
                    DetalleFactura.cantidad
                )
            )
            .join(
                Factura,
                Factura.id
                == DetalleFactura.facturaId
            )
            .filter(
                Factura.estadoFactura
                == EstadoFacturaEnum.PAGADA
            )
            .filter(
                extract(
                    "month",
                    Factura.fechaCreacion
                )
                == mes
            )
            .filter(
                extract(
                    "year",
                    Factura.fechaCreacion
                )
                == anio
            )
            .filter(
                DetalleFactura.comidaId.isnot(
                    None
                )
            )
            .scalar()
            or 0
        )

        return {
            "mes": mes,
            "anio": anio,
            "facturasPagadas": cantidad_facturas,
            "ingresosTotales": float(
                ingresos_totales
            ),
            "boletasVendidas": int(
                boletas_vendidas
            ),
            "productosVendidos": int(
                productos_vendidos
            ),
        }

    # =====================================================
    # REPORTE DE RENDIMIENTO POR MULTIPLEX
    # =====================================================

    def obtener_rendimiento_multiplex(
        self,
        mes: int,
        anio: int,
    ):

        resultado = (
            self.db.query(
                Multiplex.nombre.label(
                    "multiplex"
                ),
                func.sum(
                    DetalleFactura.subTotal
                ).label("ventas"),
                func.count(
                    func.distinct(
                        Boleta.id
                    )
                ).label(
                    "boletasVendidas"
                ),
            )
            .join(
                Sala,
                Sala.multiplexId
                == Multiplex.id
            )
            .join(
                Funcion,
                Funcion.salaId
                == Sala.id
            )
            .join(
                Boleta,
                Boleta.funcionId
                == Funcion.id
            )
            .join(
                DetalleFactura,
                DetalleFactura.boletaId
                == Boleta.id
            )
            .join(
                Factura,
                Factura.id
                == DetalleFactura.facturaId
            )
            .filter(
                Factura.estadoFactura
                == EstadoFacturaEnum.PAGADA
            )
            .filter(
                extract(
                    "month",
                    Factura.fechaCreacion
                )
                == mes
            )
            .filter(
                extract(
                    "year",
                    Factura.fechaCreacion
                )
                == anio
            )
            .group_by(
                Multiplex.nombre
            )
            .order_by(
                func.sum(
                    DetalleFactura.subTotal
                ).desc()
            )
            .all()
        )

        return [
            {
                "multiplex": fila.multiplex,
                "ventas": float(
                    fila.ventas or 0
                ),
                "boletasVendidas": int(
                    fila.boletasVendidas
                ),
            }
            for fila in resultado
        ]
    
    def obtener_salarios_empleados(self):

        salarios = (
            self.db.query(
                Contrato.salario
            )
            .filter(
                Contrato.activo.is_(True)
            )
            .all()
        )

        return [
            float(salario)
            for (salario,) in salarios
        ]
    
    def obtener_empleados_por_multiplex(self):

        resultado = (
            self.db.query(
                Multiplex.nombre,
                func.count(
                    Contrato.id
                )
            )
            .join(
                Contrato,
                Contrato.multiplexId == Multiplex.id
            )
            .filter(
                Contrato.activo.is_(True)
            )
            .group_by(
                Multiplex.nombre
            )
            .order_by(
                func.count(
                    Contrato.id
                ).desc()
            )
            .all()
        )

        return [
            {
                "multiplex": nombre,
                "cantidad": cantidad,
            }
            for nombre, cantidad in resultado
        ]
    def obtener_ventas_por_multiplex(
    self,
    mes: int,
    anio: int
):

        resultado = (
            self.db.query(
                Multiplex.nombre,
                func.sum(
                    DetalleFactura.subTotal
                )
            )
            .join(
                Sala,
                Sala.multiplexId == Multiplex.id
            )
            .join(
                Funcion,
                Funcion.salaId == Sala.id
            )
            .join(
                Boleta,
                Boleta.funcionId == Funcion.id
            )
            .join(
                DetalleFactura,
                DetalleFactura.boletaId == Boleta.id
            )
            .join(
                Factura,
                Factura.id == DetalleFactura.facturaId
            )
            .filter(
                Factura.estadoFactura ==
                EstadoFacturaEnum.PAGADA
            )
            .filter(
                extract(
                    "month",
                    Factura.fechaCreacion
                ) == mes
            )
            .filter(
                extract(
                    "year",
                    Factura.fechaCreacion
                ) == anio
            )
            .group_by(
                Multiplex.nombre
            )
            .order_by(
                func.sum(
                    DetalleFactura.subTotal
                ).desc()
            )
            .all()
        )

        return [
            {
                "multiplex": nombre,
                "ventas": float(
                    ventas or 0
                ),
            }
            for nombre, ventas in resultado
        ]