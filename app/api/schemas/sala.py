"""Sala schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class SalaCreate(BaseModel):
    """Schema para crear una nueva sala."""
    numero: int = Field(..., ge=1, le=999, description="Número de sala (1-999)")
    capacidadTotal: int = Field(..., ge=1, description="Capacidad total de la sala")
    capacidadPreferencial: int = Field(..., ge=0, description="Capacidad de sillas preferenciales")

    model_config = {
        "json_schema_extra": {
            "example": {
                "numero": 1,
                "capacidadTotal": 150,
                "capacidadPreferencial": 20
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "numero": 2,
                "capacidadTotal": 120
            }
        }
    }

    def model_post_init(self, __context):
        """Validación: si ambas capacidades están presentes, validar relación."""
        if self.capacidadPreferencial is not None and self.capacidadTotal is not None:
            if self.capacidadPreferencial > self.capacidadTotal:
                raise ValueError("capacidadPreferencial no puede exceder capacidadTotal")


class SalaResponse(BaseModel):
    """Schema de respuesta para una sala."""
    id: int
    numero: int
    capacidadTotal: int
    capacidadPreferencial: int
    activa: bool = Field(alias="estaActiva")
    multiplexId: int

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "numero": 1,
                "capacidadTotal": 150,
                "capacidadPreferencial": 20,
                "activa": True,
                "multiplexId": 1
            }
        }
    }
