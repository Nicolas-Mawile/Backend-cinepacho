from typing import List, Optional
import uuid
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field

from .sala import SalaSimpleResponse

class MultiplexCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150)
    ciudad: str = Field(..., min_length=2, max_length=100)
    direccion: str = Field(..., min_length=5, max_length=250)
    latitud: Decimal = Field(..., ge=-90, le=90)
    longitud: Decimal = Field(..., ge=-180, le=180)

class MultiplexUpdate(BaseModel):
    nombre: Optional[str] | None = Field(None, min_length=3, max_length=150)
    ciudad: Optional[str] | None = None
    direccion: Optional[str] | None = None
    latitud: Optional[Decimal] | None = None
    longitud: Optional[Decimal] | None = None

class MultiplexResponse(BaseModel):
    id: int
    nombre: str
    codigo: str
    ciudad: str
    direccion: str
    latitud: Decimal
    longitud: Decimal

    activo: bool = Field(alias="estaActivo")

    cantidad_salas: int = 0

    salas :List[SalaSimpleResponse] = []

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }