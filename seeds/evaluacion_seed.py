"""
evaluacion_seed.py
==================
Datos de prueba para los endpoints de evaluaciones.
Se ejecuta automáticamente desde seed_master al levantar la app.

  - Usa juan@gmail.com (de clientes_seed)
  - Películas Umamusume y Avengers (busca en BD o las crea)
  - 2 funciones del 28/05/2026 (ya terminadas)
  - 1 factura PAGADA (ayer) con boletas → habilita peliculas-evaluables
  - 1 factura PAGADA (hoy) con comida   → habilita servicios-evaluables
"""

from datetime import datetime, timedelta
from sqlalchemy import select

from app.database import SessionLocal
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.models.pelicula import Pelicula
from app.infrastructure.models.sala import Sala
from app.infrastructure.models.silla import Silla
from app.infrastructure.models.funcion import Funcion
from app.infrastructure.models.factura import Factura
from app.infrastructure.models.detalleFactura import DetalleFactura
from app.infrastructure.models.boleta import Boleta
from app.infrastructure.models.comida import Comida
from app.infrastructure.models.pago import Pago
from app.infrastructure.models.multiplex_cartelera import MultiplexCartelera
from app.infrastructure.models.EstadoFacturaEnum import EstadoFacturaEnum
from app.infrastructure.models.EstadoPagoEnum import EstadoPagoEnum

# ============================================================
# CONFIGURACION
# ============================================================

CLIENTE_CORREO = "juan@gmail.com"

AYER = datetime(2026, 5, 28)
MINUTOS_LIMPIEZA = 20

DATOS_PELICULAS = [
    {
        "buscar": "umamusume",
        "titulo": "Umamusume: Road to the Top",
        "duracion": 140,
        "sinopsis": "Las chicas caballo corren hacia la cima en la gran carrera final.",
        "hora": 14,
        "minuto": 0,
    },
    {
        "buscar": "avengers",
        "titulo": "Avengers: Doomsday",
        "duracion": 149,
        "sinopsis": "Los Vengadores enfrentan su mayor amenaza en una batalla por el universo.",
        "hora": 17,
        "minuto": 30,
    },
]


# ============================================================
# HELPERS
# ============================================================

def _get_cliente(db):
    cliente = db.execute(
        select(Cliente).where(Cliente.correo == CLIENTE_CORREO)
    ).scalar_one_or_none()

    if not cliente:
        raise Exception(
            f"Cliente '{CLIENTE_CORREO}' no encontrado. "
            "Ejecuta clientes_seed primero."
        )

    return cliente


def _get_or_create_pelicula(db, buscar, titulo, duracion, sinopsis):
    pelicula = db.execute(
        select(Pelicula).where(Pelicula.titulo.ilike(f"%{buscar}%"))
    ).scalars().first()

    if pelicula:
        return pelicula

    pelicula = Pelicula(
        titulo=titulo,
        duracionMinutos=duracion,
        sinopsis=sinopsis,
        estaActiva=True,
    )
    db.add(pelicula)
    db.flush()
    return pelicula


def _get_sala_con_sillas(db):
    salas = db.execute(
        select(Sala).where(Sala.estaActiva == True)
    ).scalars().all()

    for sala in salas:
        tiene_sillas = db.execute(
            select(Silla).where(Silla.salaId == sala.id).limit(1)
        ).scalar_one_or_none()
        if tiene_sillas:
            return sala

    raise Exception(
        "No hay salas activas con sillas en la BD. "
        "Ejecuta primero multiplex_seed y el seed de salas/sillas."
    )


def _ensure_cartelera(db, multiplex_id, pelicula_id):
    existente = db.execute(
        select(MultiplexCartelera).where(
            MultiplexCartelera.multiplexId == multiplex_id,
            MultiplexCartelera.peliculaId == pelicula_id,
        )
    ).scalar_one_or_none()

    if existente:
        return

    db.add(MultiplexCartelera(multiplexId=multiplex_id, peliculaId=pelicula_id))
    db.flush()


def _get_or_create_funcion(db, pelicula, sala, hora, minuto):
    fecha_inicio = AYER.replace(hour=hora, minute=minuto, second=0, microsecond=0)
    fecha_fin = fecha_inicio + timedelta(
        minutes=pelicula.duracionMinutos + MINUTOS_LIMPIEZA
    )

    existente = db.execute(
        select(Funcion).where(
            Funcion.salaId == sala.id,
            Funcion.fechaHora == fecha_inicio,
        )
    ).scalar_one_or_none()

    if existente:
        return existente

    funciones_sala = db.execute(
        select(Funcion).where(Funcion.salaId == sala.id)
    ).scalars().all()

    for f in funciones_sala:
        if fecha_inicio < f.fechaHoraFin and fecha_fin > f.fechaHora:
            raise Exception(
                f"Traslape detectado en sala {sala.id}: '{pelicula.titulo}' "
                f"({fecha_inicio} - {fecha_fin}) choca con función id={f.id}. "
                "Cambia las horas en DATOS_PELICULAS o usa otra sala."
            )

    funcion = Funcion(
        peliculaId=pelicula.id,
        salaId=sala.id,
        fechaHora=fecha_inicio,
        fechaHoraFin=fecha_fin,
        estaActiva=True,
    )
    db.add(funcion)
    db.flush()
    return funcion


def _silla_libre(db, sala_id, funcion_id):
    ocupadas = db.execute(
        select(Boleta.sillaId).where(Boleta.funcionId == funcion_id)
    ).scalars().all()

    query = select(Silla).where(
        Silla.salaId == sala_id,
        Silla.estaActiva == True,
    )
    if ocupadas:
        query = query.where(~Silla.id.in_(ocupadas))

    return db.execute(query.limit(1)).scalar_one_or_none()


def _crear_boleta_y_detalle(db, factura, funcion, sala_id):
    silla = _silla_libre(db, sala_id, funcion.id)
    if not silla:
        raise Exception(
            f"No hay sillas libres para función {funcion.id} (sala {sala_id})."
        )

    boleta = Boleta(funcionId=funcion.id, sillaId=silla.id)
    db.add(boleta)
    db.flush()

    precio = silla.tipoSilla.precio if silla.tipoSilla else 11_000.0

    db.add(DetalleFactura(
        facturaId=factura.id,
        boletaId=boleta.id,
        cantidad=1,
        precioUnitario=precio,
        subTotal=precio,
    ))
    db.flush()
    return precio


def _crear_pago(db, factura, total, fecha_pago):
    db.add(Pago(
        facturaId=factura.id,
        monto=total,
        estado=EstadoPagoEnum.PAGADO,
        metodoPago="TARJETA",
        fechaPago=fecha_pago,
        fechaExpiracion=fecha_pago + timedelta(minutes=15),
    ))
    db.flush()


def _ya_existe_boleta_pagada(db, cliente_id, funcion_id):
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


# ============================================================
# MAIN
# ============================================================

def run():
    with SessionLocal() as db:
        try:
            cliente = _get_cliente(db)
            sala = _get_sala_con_sillas(db)

            for datos in DATOS_PELICULAS:
                pelicula = _get_or_create_pelicula(
                    db,
                    buscar=datos["buscar"],
                    titulo=datos["titulo"],
                    duracion=datos["duracion"],
                    sinopsis=datos["sinopsis"],
                )
                _ensure_cartelera(db, sala.multiplexId, pelicula.id)
                funcion = _get_or_create_funcion(
                    db, pelicula, sala,
                    hora=datos["hora"],
                    minuto=datos["minuto"],
                )

                if not _ya_existe_boleta_pagada(db, cliente.id, funcion.id):
                    factura = Factura(
                        clienteId=cliente.id,
                        subTotal=0,
                        descuento=0,
                        total=0,
                        fechaCreacion=AYER,
                        fechaExpiracionReserva=AYER + timedelta(minutes=15),
                        codigoTransaccion=f"TX-EVAL-{pelicula.id}",
                        estadoFactura=EstadoFacturaEnum.PAGADA,
                    )
                    db.add(factura)
                    db.flush()

                    subtotal = _crear_boleta_y_detalle(db, factura, funcion, sala.id)
                    factura.subTotal = subtotal
                    factura.total = subtotal
                    db.flush()

                    _crear_pago(db, factura, subtotal, AYER)

            comida = db.execute(
                select(Comida).where(Comida.estaActiva == True).limit(1)
            ).scalar_one_or_none()

            if comida:
                factura_snack_existente = db.execute(
                    select(Factura).where(
                        Factura.codigoTransaccion == "TX-EVAL-SERVICIOS",
                        Factura.clienteId == cliente.id,
                    )
                ).scalar_one_or_none()

                if not factura_snack_existente:
                    ahora = datetime.now()
                    factura_snack = Factura(
                        clienteId=cliente.id,
                        subTotal=comida.precio,
                        descuento=0,
                        total=comida.precio,
                        fechaCreacion=ahora,
                        fechaExpiracionReserva=ahora + timedelta(minutes=15),
                        codigoTransaccion="TX-EVAL-SERVICIOS",
                        estadoFactura=EstadoFacturaEnum.PAGADA,
                    )
                    db.add(factura_snack)
                    db.flush()

                    db.add(DetalleFactura(
                        facturaId=factura_snack.id,
                        comidaId=comida.id,
                        cantidad=1,
                        precioUnitario=comida.precio,
                        subTotal=comida.precio,
                    ))
                    db.flush()

                    _crear_pago(db, factura_snack, comida.precio, ahora)

            db.commit()

        except Exception as e:
            db.rollback()
            raise
