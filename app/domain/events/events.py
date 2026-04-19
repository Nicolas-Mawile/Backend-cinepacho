"""Domain event dataclasses."""

from dataclasses import dataclass


@dataclass
class ReservaIniciada:
    reserva_id: int


@dataclass
class PagoConfirmado:
    pago_id: int
