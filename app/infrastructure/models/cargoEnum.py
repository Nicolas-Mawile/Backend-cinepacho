from enum import Enum

class CargoEnum(Enum):
    director = "director"
    cajero = "cajero"
    despachador_comida = "despachador_comida"
    encargado_sala = "encargado_sala"
    aseador = "aseador"
    administrador = "administrador" # Para compatibilidad con contrato POST /empleados
