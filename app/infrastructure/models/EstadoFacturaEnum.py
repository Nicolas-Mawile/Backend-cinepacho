from enum import Enum

class EstadoFacturaEnum(str, Enum):
    RESERVADA = "RESERVADA"
    PAGADA = "PAGADA"
    CANCELADA = "CANCELADA"