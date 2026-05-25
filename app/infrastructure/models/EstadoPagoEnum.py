import enum
class EstadoPagoEnum(enum.Enum):
    # Pago creado pero aún no confirmado
    PENDIENTE = "PENDIENTE"
    # Usuario confirmó correctamente
    PAGADO = "PAGADO"
    # Reserva expiró antes de confirmar
    EXPIRADO = "EXPIRADO"
    # Cancelado manualmente/error
    CANCELADO = "CANCELADO"