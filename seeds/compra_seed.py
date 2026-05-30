"""Seed data for compras."""

import random
from datetime import datetime, timedelta

from sqlalchemy import select

from app.database import SessionLocal
from app.utils.timezone import nowColombia
from app.infrastructure.models.factura import Factura
from app.infrastructure.models.detalleFactura import DetalleFactura
from app.infrastructure.models.boleta import Boleta
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.silla import Silla
from app.infrastructure.models.comida import Comida
from app.infrastructure.models.pago import Pago

from app.infrastructure.models.EstadoFacturaEnum import (
    EstadoFacturaEnum
)

from app.infrastructure.models.EstadoPagoEnum import (
    EstadoPagoEnum
)


CANTIDAD_FACTURAS = 25

METODOS_PAGO = [
    "TARJETA",
    "PSE",
    "NEQUI",
    "EFECTIVO"
]


def get_available_sillas(
    db,
    funcion_id
):
    """
    Retorna sillas disponibles
    para una función.
    """

    funcion = db.execute(
        select(Funcion).where(
            Funcion.id == funcion_id
        )
    ).scalar_one_or_none()

    if not funcion:
        return []

    sala_id = funcion.salaId

    sillas_ocupadas = db.execute(
        select(Boleta.sillaId).where(
            Boleta.funcionId == funcion_id
        )
    ).scalars().all()

    query = select(Silla).where(
        Silla.salaId == sala_id
    )

    if sillas_ocupadas:
        query = query.where(
            ~Silla.id.in_(sillas_ocupadas)
        )

    sillas = db.execute(query).scalars().all()

    return sillas


def create_boleta(
    db,
    funcion,
    silla
):

    boleta_existente = db.execute(
        select(Boleta).where(
            Boleta.funcionId == funcion.id,
            Boleta.sillaId == silla.id
        )
    ).scalar_one_or_none()

    if boleta_existente:
        return None

    boleta = Boleta(
        funcionId=funcion.id,
        sillaId=silla.id
    )

    db.add(boleta)
    db.flush()

    return boleta


def create_detalle_boleta(
    db,
    factura,
    boleta
):

    precio = boleta.silla.tipoSilla.precio

    detalle = DetalleFactura(
        facturaId=factura.id,
        boletaId=boleta.id,
        cantidad=1,
        precioUnitario=precio,
        subTotal=precio
    )

    db.add(detalle)

    return precio


def create_detalle_comida(
    db,
    factura,
    comida,
    cantidad
):

    subtotal = comida.precio * cantidad

    detalle = DetalleFactura(
        facturaId=factura.id,
        comidaId=comida.id,
        cantidad=cantidad,
        precioUnitario=comida.precio,
        subTotal=subtotal
    )

    db.add(detalle)

    return subtotal


def create_pago(
    db,
    factura,
    total,
    estado
):

    pago = Pago(
        facturaId=factura.id,
        monto=total,
        estado=estado,
        metodoPago=random.choice(METODOS_PAGO),
        fechaPago=(
            nowColombia()
            if estado == EstadoPagoEnum.PAGADO
            else None
        ),
        fechaExpiracion=(
            nowColombia()
            + timedelta(minutes=15)
        ),
        recompensaId=None,
    )

    db.add(pago)


def calculate_totals(
    subtotal
):

    descuento = 0

    total = subtotal - descuento

    return descuento, total


def validate_integrity(db):

    facturas = db.execute(
        select(Factura)
    ).scalars().all()

    for factura in facturas:

        if factura.total < 0:

            raise Exception(
                f"Factura inválida ID {factura.id}"
            )

        if not factura.detalles:

            raise Exception(
                f"Factura sin detalles ID {factura.id}"
            )

        total_detalles = sum(
            detalle.subTotal
            for detalle in factura.detalles
        )

        if round(total_detalles, 2) != round(factura.subTotal, 2):

            raise Exception(
                f"Subtotal inconsistente "
                f"Factura {factura.id}"
            )

    print("✅ Validación compras completada")


def run():

    with SessionLocal() as db:

        try:

            print(
                "\n🛒 Iniciando seed compras...\n"
            )

            clientes = db.execute(
                select(Cliente).where(
                    Cliente.estaActivo == True
                )
            ).scalars().all()

            funciones = db.execute(
                select(Funcion).where(
                    Funcion.estaActiva == True
                )
            ).scalars().all()

            comidas = db.execute(
                select(Comida)
            ).scalars().all()

            if not clientes:
                raise Exception(
                    "No existen clientes activos"
                )

            if not funciones:
                raise Exception(
                    "No existen funciones activas"
                )

            if not comidas:
                print(
                    "⚠️ No existen comidas, "
                    "se crearán compras solo con boletas"
                )

            facturas_existentes = db.execute(
                select(Factura)
            ).scalars().all()

            if len(facturas_existentes) >= CANTIDAD_FACTURAS:

                print(
                    "ℹ️ Ya existen suficientes "
                    "facturas generadas"
                )

                return

            count = 0

            for _ in range(CANTIDAD_FACTURAS):

                cliente = random.choice(clientes)

                estado_factura = random.choice([
                    EstadoFacturaEnum.PAGADA,
                    EstadoFacturaEnum.PAGADA,
                    EstadoFacturaEnum.PAGADA,
                    EstadoFacturaEnum.RESERVADA,
                    EstadoFacturaEnum.CANCELADA
                ])

                factura = Factura(
                    clienteId=cliente.id,
                    subTotal=0,
                    descuento=0,
                    total=0,
                    fechaCreacion=(
                        datetime.now()
                        - timedelta(
                            days=random.randint(0, 7)
                        )
                    ),
                    fechaExpiracionReserva=(
                        datetime.now()
                        + timedelta(minutes=15)
                    ),
                    codigoTransaccion=(
                        f"TX-"
                        f"{random.randint(100000,999999)}"
                    ),
                    estadoFactura=estado_factura
                )

                db.add(factura)
                db.flush()

                subtotal = 0
                cantidad_boletas = 0
                cantidad_comidas = 0

                # -----------------------------------
                # BOLETAS
                # -----------------------------------

                cantidad_boletas_seed = random.randint(1, 4)

                for _ in range(cantidad_boletas_seed):

                    funcion = random.choice(funciones)

                    sillas_disponibles = (
                        get_available_sillas(
                            db,
                            funcion.id
                        )
                    )

                    if not sillas_disponibles:
                        continue

                    silla = random.choice(
                        sillas_disponibles
                    )

                    boleta = create_boleta(
                        db,
                        funcion,
                        silla
                    )

                    if not boleta:
                        continue

                    subtotal += create_detalle_boleta(
                        db,
                        factura,
                        boleta
                    )

                    cantidad_boletas += 1

                # -----------------------------------
                # COMIDAS
                # -----------------------------------

                if comidas:

                    cantidad_comidas_seed = (
                        random.randint(0, 3)
                    )

                    for _ in range(
                        cantidad_comidas_seed
                    ):

                        comida = random.choice(
                            comidas
                        )

                        cantidad = random.randint(
                            1,
                            2
                        )

                        subtotal += create_detalle_comida(
                            db,
                            factura,
                            comida,
                            cantidad
                        )

                        cantidad_comidas += cantidad

                # Evitar facturas vacías

                if subtotal <= 0:

                    db.delete(factura)
                    continue

                descuento, total = (
                    calculate_totals(subtotal)
                )

                factura.subTotal = subtotal
                factura.descuento = descuento
                factura.total = total

                # -----------------------------------
                # PAGOS
                # -----------------------------------

                estado_pago = {
                    EstadoFacturaEnum.PAGADA:
                        EstadoPagoEnum.PAGADO,

                    EstadoFacturaEnum.RESERVADA:
                        EstadoPagoEnum.PENDIENTE,

                    EstadoFacturaEnum.CANCELADA:
                        EstadoPagoEnum.CANCELADO
                }[estado_factura]

                create_pago(
                    db,
                    factura,
                    total,
                    estado_pago
                )

                # -----------------------------------
                # PUNTOS
                # -----------------------------------

                if estado_factura == EstadoFacturaEnum.PAGADA:

                    cliente.puntosAcumulados += (
                        cantidad_boletas * 10
                    )

                    cliente.puntosAcumulados += (
                        cantidad_comidas * 5
                    )

                count += 1

            db.commit()

            validate_integrity(db)

            print(
                f"\n✅ Seed compras completado "
                f"({count} facturas creadas)\n"
            )

        except Exception as e:

            db.rollback()

            print(
                f"\n❌ Error seed compras:\n{e}"
            )

            raise e


if __name__ == "__main__":

    run()