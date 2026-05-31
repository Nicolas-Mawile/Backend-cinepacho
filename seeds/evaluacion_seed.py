"""
evaluacion_seed.py
==================
Crea compras históricas y evaluaciones de prueba para los 3 clientes de test.

  - Juan Gómez       → Umamusume + Avengers: Doomsday
  - Laura Ramírez     → Misión Imposible + Paddington en Perú
  - Nicolas Castro    → Sonic 3 + El Señor de los Anillos

Cada cliente recibe:
  • 1 factura PAGADA con boleta por cada película vista
  • 1 factura PAGADA con snacks (habilita evaluaciones de servicio)
  • Evaluaciones de película y de servicios

Requiere: clientes_seed, funciones_seed (DIAS_PASADOS activo), comidas_seed, servicios_seed.
"""

from datetime import datetime, timedelta
from sqlalchemy import select

from app.database import SessionLocal
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.models.pelicula import Pelicula
from app.infrastructure.models.silla import Silla
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.factura import Factura
from app.infrastructure.models.detalleFactura import DetalleFactura
from app.infrastructure.models.boleta import Boleta
from app.infrastructure.models.comida import Comida
from app.infrastructure.models.pago import Pago
from app.infrastructure.models.evaluacion import Evaluacion
from app.infrastructure.models.servicio import Servicio
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum
from app.infrastructure.models.EstadoPagoEnum import EstadoPagoEnum


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE EVALUACIONES POR CLIENTE
# ─────────────────────────────────────────────────────────────────────────────

ASIGNACIONES = [
    {
        "correo": "juan@gmail.com",
        "funciones": [
            {
                "pelicula_keyword": "umamusume",
                "comentario": "Animación hermosa y muy emotiva. Una obra maestra del género.",
                "puntuacion": 5,
            },
            {
                "pelicula_keyword": "avengers",
                "comentario": "Increíble batalla final. Efectos especiales al máximo nivel.",
                "puntuacion": 5,
            },
        ],
        "snacks": ["Pop Corn Sal Grande", "Gaseosa Mediana"],
        "servicios": [
            {
                "comentario": "Excelente atención en caja, muy rápido y amable.",
                "puntuacion": 5,
            },
            {
                "comentario": "La sala estaba impecable y muy cómoda.",
                "puntuacion": 5,
            },
            {
                "comentario": "Sonido e imagen perfectos durante toda la función.",
                "puntuacion": 5,
            },
        ],
    },
    {
        "correo": "laura@gmail.com",
        "funciones": [
            {
                "pelicula_keyword": "misión imposible",
                "comentario": "Ethan Hunt nunca decepciona. Adrenalina pura de principio a fin.",
                "puntuacion": 5,
            },
            {
                "pelicula_keyword": "paddington",
                "comentario": "Muy tierna y divertida. Perfecta para toda la familia.",
                "puntuacion": 4,
            },
        ],
        "snacks": ["Nachos con Queso", "Gaseosa Grande"],
        "servicios": [
            {
                "comentario": "Buen servicio, aunque había bastante fila en caja.",
                "puntuacion": 4,
            },
            {
                "comentario": "La sala estaba bastante cómoda y limpia.",
                "puntuacion": 4,
            },
            {
                "comentario": "Proyección excelente, sin interrupciones.",
                "puntuacion": 5,
            },
        ],
    },
    {
        "correo": "nicolascr333@gmail.com",
        "funciones": [
            {
                "pelicula_keyword": "sonic",
                "comentario": "Muy divertida para toda la familia. Shadow estuvo increíble.",
                "puntuacion": 4,
            },
            {
                "pelicula_keyword": "señor de los anillos",
                "comentario": "Épica animación. Una joya para los fans de Tolkien.",
                "puntuacion": 5,
            },
        ],
        "snacks": ["Hot Dog Especial", "Pop Corn Mixto Grande"],
        "servicios": [
            {
                "comentario": "Servicio muy eficiente y cordial en el despachador.",
                "puntuacion": 5,
            },
            {
                "comentario": "La sala estaba bien, aunque un poco fría.",
                "puntuacion": 4,
            },
            {
                "comentario": "Calidad de audio excepcional en esta sala.",
                "puntuacion": 5,
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _get_cliente(db, correo: str):
    return db.execute(
        select(Cliente).where(Cliente.correo == correo)
    ).scalar_one_or_none()


def _find_past_funcion(db, pelicula_keyword: str):
    """Devuelve la función pasada más reciente para la película indicada."""
    ahora = datetime.now()
    return db.execute(
        select(Funcion)
        .join(Pelicula, Pelicula.id == Funcion.peliculaId)
        .where(
            Funcion.fechaHoraFin < ahora,
            Funcion.estaActiva == True,
            Pelicula.titulo.ilike(f"%{pelicula_keyword}%"),
        )
        .order_by(Funcion.fechaHora.desc())
        .limit(1)
    ).scalar_one_or_none()


def _silla_libre(db, sala_id: int, funcion_id: int):
    ocupadas = db.execute(
        select(Boleta.sillaId).where(Boleta.funcionId == funcion_id)
    ).scalars().all()

    q = select(Silla).where(Silla.salaId == sala_id, Silla.estaActiva == True)
    if ocupadas:
        q = q.where(~Silla.id.in_(ocupadas))
    return db.execute(q.limit(1)).scalar_one_or_none()


def _ya_existe_boleta_pagada(db, cliente_id: int, funcion_id: int):
    return db.execute(
        select(Boleta)
        .join(DetalleFactura, DetalleFactura.boletaId == Boleta.id)
        .join(Factura, Factura.id == DetalleFactura.facturaId)
        .where(
            Boleta.funcionId == funcion_id,
            Factura.clienteId == cliente_id,
            Factura.estadoFactura == EstadoFacturaEnum.PAGADA,
        )
    ).scalar_one_or_none()


def _crear_compra_boleta(db, cliente, funcion):
    """Crea factura + boleta + pago PAGADO para una función pasada."""
    silla = _silla_libre(db, funcion.salaId, funcion.id)
    if not silla:
        return None

    precio = float(silla.tipoSilla.precio) if silla.tipoSilla else 11_000.0
    fecha_pago = funcion.fechaHora

    factura = Factura(
        clienteId=cliente.id,
        subTotal=precio,
        descuento=0,
        total=precio,
        fechaCreacion=fecha_pago,
        fechaExpiracionReserva=fecha_pago + timedelta(minutes=15),
        codigoTransaccion=f"TX-EVAL-{cliente.id}-{funcion.id}",
        estadoFactura=EstadoFacturaEnum.PAGADA,
    )
    db.add(factura)
    db.flush()

    boleta = Boleta(funcionId=funcion.id, sillaId=silla.id)
    db.add(boleta)
    db.flush()

    db.add(DetalleFactura(
        facturaId=factura.id,
        boletaId=boleta.id,
        cantidad=1,
        precioUnitario=precio,
        subTotal=precio,
    ))

    db.add(Pago(
        facturaId=factura.id,
        monto=precio,
        estado=EstadoPagoEnum.PAGADO,
        metodoPago="TARJETA",
        fechaPago=fecha_pago,
        fechaExpiracion=fecha_pago + timedelta(minutes=15),
    ))
    db.flush()
    return factura


def _ya_existe_evaluacion_pelicula(db, cliente_id, funcion_id, pelicula_id):
    return db.execute(
        select(Evaluacion).where(
            Evaluacion.cliente_id == cliente_id,
            Evaluacion.funcion_id == funcion_id,
            Evaluacion.pelicula_id == pelicula_id,
        )
    ).scalar_one_or_none()


def _ya_existe_evaluacion_servicio(db, cliente_id, factura_id, servicio_id):
    return db.execute(
        select(Evaluacion).where(
            Evaluacion.cliente_id == cliente_id,
            Evaluacion.factura_id == factura_id,
            Evaluacion.servicio_id == servicio_id,
        )
    ).scalar_one_or_none()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def run():
    with SessionLocal() as db:
        try:
            servicios = db.execute(select(Servicio)).scalars().all()
            todas_comidas = db.execute(
                select(Comida).where(Comida.estaActiva == True)
            ).scalars().all()
            comidas_por_nombre = {c.nombre: c for c in todas_comidas}

            for asignacion in ASIGNACIONES:
                correo = asignacion["correo"]
                cliente = _get_cliente(db, correo)
                if not cliente:
                    print(f"⚠️  Cliente '{correo}' no encontrado, saltando.")
                    continue

                # ── BOLETAS + EVALUACIONES DE PELÍCULAS ──────────────────────
                for datos_fn in asignacion["funciones"]:
                    funcion = _find_past_funcion(db, datos_fn["pelicula_keyword"])
                    if not funcion:
                        print(
                            f"⚠️  Sin función pasada para "
                            f"'{datos_fn['pelicula_keyword']}' — saltando."
                        )
                        continue

                    if not _ya_existe_boleta_pagada(db, cliente.id, funcion.id):
                        factura = _crear_compra_boleta(db, cliente, funcion)
                        if factura:
                            cliente.puntosAcumulados += 10
                            db.flush()

                    if not _ya_existe_evaluacion_pelicula(
                        db, cliente.id, funcion.id, funcion.peliculaId
                    ):
                        db.add(Evaluacion(
                            cliente_id=cliente.id,
                            funcion_id=funcion.id,
                            pelicula_id=funcion.peliculaId,
                            comentario=datos_fn["comentario"],
                            puntuacion=datos_fn["puntuacion"],
                        ))
                        db.flush()

                # ── COMPRA DE SNACKS ──────────────────────────────────────────
                tx_snack = f"TX-SNACK-{cliente.id}"
                factura_snack = db.execute(
                    select(Factura).where(
                        Factura.codigoTransaccion == tx_snack,
                        Factura.clienteId == cliente.id,
                    )
                ).scalar_one_or_none()

                if not factura_snack and todas_comidas:
                    snack_items = [
                        comidas_por_nombre[n]
                        for n in asignacion["snacks"]
                        if n in comidas_por_nombre
                    ]
                    if not snack_items:
                        snack_items = todas_comidas[:2]

                    subtotal = sum(float(c.precio) for c in snack_items)
                    fecha_snack = datetime.now() - timedelta(days=5)

                    factura_snack = Factura(
                        clienteId=cliente.id,
                        subTotal=subtotal,
                        descuento=0,
                        total=subtotal,
                        fechaCreacion=fecha_snack,
                        fechaExpiracionReserva=fecha_snack + timedelta(minutes=15),
                        codigoTransaccion=tx_snack,
                        estadoFactura=EstadoFacturaEnum.PAGADA,
                    )
                    db.add(factura_snack)
                    db.flush()

                    for comida in snack_items:
                        db.add(DetalleFactura(
                            facturaId=factura_snack.id,
                            comidaId=comida.id,
                            cantidad=1,
                            precioUnitario=float(comida.precio),
                            subTotal=float(comida.precio),
                        ))
                    db.flush()

                    db.add(Pago(
                        facturaId=factura_snack.id,
                        monto=subtotal,
                        estado=EstadoPagoEnum.PAGADO,
                        metodoPago="NEQUI",
                        fechaPago=fecha_snack,
                        fechaExpiracion=fecha_snack + timedelta(minutes=15),
                    ))
                    db.flush()

                    cliente.puntosAcumulados += 5 * len(snack_items)
                    db.flush()

                # ── EVALUACIONES DE SERVICIOS ─────────────────────────────────
                if factura_snack and servicios:
                    datos_servicios = asignacion["servicios"]
                    for i, servicio in enumerate(servicios):
                        if i >= len(datos_servicios):
                            break
                        if not _ya_existe_evaluacion_servicio(
                            db, cliente.id, factura_snack.id, servicio.id
                        ):
                            db.add(Evaluacion(
                                cliente_id=cliente.id,
                                factura_id=factura_snack.id,
                                servicio_id=servicio.id,
                                comentario=datos_servicios[i]["comentario"],
                                puntuacion=datos_servicios[i]["puntuacion"],
                            ))
                            db.flush()

            db.commit()
            print("✅ evaluacion_seed completado")

        except Exception as e:
            db.rollback()
            raise
