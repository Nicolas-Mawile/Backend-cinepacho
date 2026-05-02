import enum

class EstadoPagoEnum(enum.Enum):
    PENDIENTE = "PENDIENTE"
    PAGADO = "PAGADO"
    CANCELADO = "CANCELADO"