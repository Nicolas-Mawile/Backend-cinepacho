"""Factura service — consultas de facturas, resúmenes y boletas."""
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.models.factura import Factura
from app.infrastructure.models.boleta import Boleta
from app.infrastructure.models.detalleFactura import DetalleFactura
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum
from app.infrastructure.repositories.factura_repository import FacturaRepository


class FacturaService:
    """Consultas sobre facturas, resúmenes de compra y boletas."""

    def __init__(self, db: Session):
        self.db = db
        self.factura_repository = FacturaRepository(db)

    # =========================================================
    # RESUMEN (accesible para invitados también)
    # =========================================================

    def obtener_resumen(self, factura_id: int, cliente_id: int | None):
        factura = (
            self.db.query(Factura)
            .options(
                joinedload(Factura.detalles).joinedload(DetalleFactura.boleta).joinedload(Boleta.silla),
                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.funcion)
                .joinedload(Funcion.pelicula),
                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.funcion)
                .joinedload(Funcion.sala),
                joinedload(Factura.detalles).joinedload(DetalleFactura.comida),
            )
            .filter(Factura.id == factura_id)
            .first()
        )

        if not factura:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        # Si hay cliente autenticado, verificar propiedad
        # Si no hay cliente autenticado (invitado), permitir acceso por id de factura
        if cliente_id is not None and factura.clienteId != cliente_id:
            raise HTTPException(
                status_code=403,
                detail="No puede acceder a esta factura",
            )

        boletas = []
        comidas = []
        for detalle in factura.detalles:
            if detalle.boleta:
                b = detalle.boleta
                boletas.append(
                    {
                        "boletaId": b.id,
                        "funcionId": b.funcion.id,
                        "pelicula": b.funcion.pelicula.titulo,
                        "sala": f"Sala {b.funcion.sala.numero}",
                        "fechaHora": b.funcion.fechaHora,
                        "sillaId": b.silla.id,
                        "fila": str(b.silla.fila),
                        "columna": b.silla.columna,
                        "subtotal": detalle.subTotal,
                    }
                )
            if detalle.comida:
                c = detalle.comida
                comidas.append(
                    {
                        "comidaId": c.id,
                        "nombre": c.nombre,
                        "cantidad": detalle.cantidad,
                        "precioUnitario": detalle.precioUnitario,
                        "subtotal": detalle.subTotal,
                    }
                )

        return {
            "facturaId": factura.id,
            "estado": factura.estadoFactura,
            "subtotal": factura.subTotal,
            "descuento": factura.descuento,
            "total": factura.total,
            "expira": factura.fechaExpiracionReserva,
            "boletas": boletas,
            "comidas": comidas,
        }

    # =========================================================
    # CONFIRMACIÓN
    # =========================================================

    def obtener_confirmacion(self, factura_id: int):
        factura = (
            self.db.query(Factura)
            .options(
                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.funcion)
                .joinedload(Funcion.pelicula),

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.boleta)
                .joinedload(Boleta.silla),

                joinedload(Factura.detalles)
                .joinedload(DetalleFactura.comida),
            )
                        .filter(Factura.id == factura_id)
            .first()
        )

        if not factura:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        if factura.estadoFactura != EstadoFacturaEnum.PAGADA:
            raise HTTPException(status_code=400, detail="La factura aún no ha sido pagada")

        boletas = []
        comidas = []
        for detalle in factura.detalles:
            if detalle.boleta:
                b = detalle.boleta
                boletas.append(
                    {
                        "boletaId": b.id,
                        "funcionId": b.funcion.id,
                        "pelicula": b.funcion.pelicula.titulo,
                        "sala": f"Sala {b.funcion.sala.numero}",
                        "fechaHora": b.funcion.fechaHora,
                        "sillaId": b.silla.id,
                        "fila": str(b.silla.fila),
                        "columna": b.silla.columna,
                    }
                )
            if detalle.comida:
                c = detalle.comida
                comidas.append(
                    {
                        "comidaId": c.id,
                        "nombre": c.nombre,
                        "cantidad": detalle.cantidad,
                        "subtotal": detalle.subTotal,
                    }
                )

        return {
            "factura": {
                "id": factura.id,
                "total": factura.total,
                "estado": factura.estadoFactura,
                "codigoTransaccion": factura.codigoTransaccion,
                "fecha": factura.fechaCreacion,
            },
            "boletas": boletas,
            "comidas": comidas,
        }

    # =========================================================
    # MIS BOLETAS
    # =========================================================

    def obtener_mis_boletas(self, cliente_id: int):

        facturas = (
            self.db.query(Factura)
            .filter(
                Factura.clienteId == cliente_id,
                Factura.estadoFactura == EstadoFacturaEnum.PAGADA,
            )
            .order_by(Factura.fechaCreacion.desc())
            .all()
        )

        resultado = []

        for factura in facturas:

            for detalle in factura.detalles:

                if not detalle.boleta:
                    continue

                boleta = detalle.boleta

                funcion = boleta.funcion

                resultado.append({
                            "boletaId": boleta.id,
                            "facturaId": factura.id,
                            "funcionId": funcion.id,
                            "pelicula": funcion.pelicula.titulo,
                            "sala": str(funcion.sala.numero),
                            "fechaHora": funcion.fechaHora,
                            "sillaId": boleta.silla.id,
                            "fila": boleta.silla.fila,
                            "columna": boleta.silla.columna,
                            "fechaCompra": factura.fechaCreacion,
                        })

        return resultado

    # =========================================================
    # BOLETAS DE UNA FACTURA ESPECÍFICA
    # =========================================================

    def obtener_boletas_factura(
    self,
    factura_id: int,
    cliente_id: int,
):

        factura = (
            self.db.query(Factura)
            .filter(
                Factura.id == factura_id,
                Factura.clienteId == cliente_id,
            )
            .first()
        )

        if not factura:
            raise HTTPException(
                status_code=404,
                detail="Factura no encontrada",
            )

        if factura.estadoFactura != EstadoFacturaEnum.PAGADA:
            raise HTTPException(
                status_code=400,
                detail="La factura aún no está pagada",
            )

        boletas = []

        for detalle in factura.detalles:

            if not detalle.boleta:
                continue

            boleta = detalle.boleta

            funcion = boleta.funcion

            boletas.append({
                            "boletaId": boleta.id,
                            "pelicula": funcion.pelicula.titulo,
                            "sala": str(funcion.sala.numero),
                            "fechaHora": funcion.fechaHora,
                            "fila": str(boleta.silla.fila),
                            "columna": boleta.silla.columna,
                        })

        return {
                "facturaId": factura.id,
                "codigoTransaccion": factura.codigoTransaccion,
                "estado": factura.estadoFactura.value,
                "fechaCompra": factura.fechaCreacion,
                "total": factura.total,
                "boletas": boletas,
            }