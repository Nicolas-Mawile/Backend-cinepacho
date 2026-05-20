"""Schemas for Empleado entity."""

from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import List, Optional
from app.infrastructure.models.cargoEnum import CargoEnum

class EmpleadoBase(BaseModel):
    id: int
    nombres: str
    apellidos: str
    correo: EmailStr
    telefono: str

class EmpleadoCrearRequest(BaseModel):
    nombres: str
    apellidos: str
    correo: EmailStr
    telefono: str
    password: str = Field(..., min_length=8)
    cargo: CargoEnum
    salario: float
    multiplexId: int

class EmpleadoUpdate(BaseModel):
    cargo: Optional[CargoEnum] = None
    salario: Optional[float] = None
    multiplex_id: Optional[int] = None

class EmpleadoResponse(BaseModel):
    id: int
    nombres: str
    apellidos: str
    correo: EmailStr
    telefono: str
    correoLaboral: EmailStr
    cargoActual: Optional[CargoEnum]
    activo: bool

    model_config = {
        "from_attributes": True
    }

class EmpleadoDetalle(BaseModel):
    """
    Response detallado de empleado.
    """
    id: int
    nombres: str
    apellidos: str
    correo: EmailStr
    telefono: Optional[str]
    codigoEmpleado: str
    correoLaboral: EmailStr
    cargoActual: Optional[CargoEnum]
    multiplexActual: Optional[str]
    salarioActual: Optional[float]
    activo: bool
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class EmpleadoListElement(BaseModel):
    id: int
    nombres: str
    apellidos: str
    codigoEmpleado : str
    cargoActual: Optional[CargoEnum]
    multiplexActual: str | None = None
    activo: bool
    model_config = {
        "from_attributes": True
    }

class EmpleadoPaginated(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    data: List[EmpleadoListElement]

class CambiarEstadoEmpleadoRequest(BaseModel):
    """
    Request para activar/desactivar empleado.
    """
    activo: bool