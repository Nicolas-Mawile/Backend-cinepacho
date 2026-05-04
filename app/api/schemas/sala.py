"""Sala schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class SillaCreate(BaseModel):
    """Schema para crear o actualizar sillas dentro de una sala."""
    tipo_silla: str = Field(..., min_length=1, description="Tipo de silla, por ejemplo preferencial o regular")
    fila_silla: int = Field(..., ge=1, description="Fila de la silla")
    columna_silla: int = Field(..., ge=1, description="Columna de la silla")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tipo_silla": "preferencial",
                "fila_silla": 1,
                "columna_silla": 1
            }
        }
    }


class SalaCreate(BaseModel):
    """Schema para crear una nueva sala."""
    numero: Optional[int] = Field(None, ge=1, le=999, description="Número de sala (1-999), se asigna automáticamente si no se proporciona")
    capacidadTotal: int = Field(..., ge=1, description="Capacidad total de la sala")
    capacidadPreferencial: int = Field(..., ge=0, description="Capacidad de sillas preferenciales")
    sillas: List[SillaCreate] = Field(default_factory=list, description="Lista de sillas de la sala")

    model_config = {
        "json_schema_extra": {
            "example": {
                "numero": 1,
                "capacidadTotal": 60,
                "capacidadPreferencial": 20,
                "sillas": [
                    {"tipo_silla": "preferencial", "fila_silla": 1, "columna_silla": 1},
                    {"tipo_silla": "regular", "fila_silla": 1, "columna_silla": 2}
                ]
            }
        }
    }

    def model_post_init(self, __context):
        """Validación: capacidad preferencial no puede exceder capacidad total."""
        if self.capacidadPreferencial > self.capacidadTotal:
            raise ValueError("capacidadPreferencial no puede exceder capacidadTotal")


class SalaUpdate(BaseModel):
    """Schema para actualizar una sala."""
    numero: Optional[int] = Field(None, ge=1, le=999, description="Número de sala")
    capacidadTotal: Optional[int] = Field(None, ge=1, description="Capacidad total")
    capacidadPreferencial: Optional[int] = Field(None, ge=0, description="Capacidad preferencial")
    sillas: Optional[List[SillaCreate]] = Field(None, description="Lista de sillas de la sala")

    model_config = {
        "json_schema_extra": {
            "example": {
                "numero": 2,
                "capacidadTotal": 60,
                "sillas": [
                    {"tipo_silla": "preferencial", "fila_silla": 1, "columna_silla": 1},
                    {"tipo_silla": "regular", "fila_silla": 1, "columna_silla": 2}
                ]
            }
        }
    }

    def model_post_init(self, __context):
        """Validación: si ambas capacidades están presentes, validar relación."""
        if self.capacidadPreferencial is not None and self.capacidadTotal is not None:
            if self.capacidadPreferencial > self.capacidadTotal:
                raise ValueError("capacidadPreferencial no puede exceder capacidadTotal")


class SillaResponse(BaseModel):
    """Schema de respuesta para una silla."""
    tipo_silla: str
    fila_silla: int = Field(alias="fila")
    columna_silla: int = Field(alias="columna")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class SalaResponse(BaseModel):
    """Schema de respuesta para una sala."""
    id: int
    numero: int
    capacidadTotal: int
    capacidadPreferencial: int
    activa: bool = Field(alias="estaActiva")
    cantidad_sillas: int
    multiplexId: int
    sillas: List[SillaResponse] = []

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "numero": 1,
                "capacidadTotal": 60,
                "capacidadPreferencial": 20,
                "activa": True,
                "cantidad_sillas": 60,
                "multiplexId": 1,
                "sillas": [
                    {"tipo_silla": "preferencial", "fila_silla": 1, "columna_silla": 1},
                    {"tipo_silla": "regular", "fila_silla": 1, "columna_silla": 2}
                ]
            }
        }
    }
