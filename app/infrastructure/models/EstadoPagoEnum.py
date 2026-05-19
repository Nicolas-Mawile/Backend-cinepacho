import enum
class EstadoPagoEnum(enum.Enum):
    # Pago creado pero aún no confirmado
    PENDIENTE = "PENDIENTE"
    # Usuario confirmó correctamente
    APROBADO = "APROBADO"
    # Reserva expiró antes de confirmar
    EXPIRADO = "EXPIRADO"
    # Cancelado manualmente/error
    CANCELADO = "CANCELADO"