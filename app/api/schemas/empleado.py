"""Schemas for Empleado entity."""

from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import List, Optional
from app.infrastructure.models.cargoEnum import CargoEnum

class EmpleadoBase(BaseModel):
    primer_nombre: str
    segundo_nombre: Optional[str] = None
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    cedula_ciudadania: str
    fecha_nacimiento: date
    telefono: str
    email: EmailStr
    cargo: CargoEnum
    salario: float
    multiplex_id: int

class EmpleadoCreate(EmpleadoBase):
    pass

class EmpleadoUpdate(BaseModel):
    cargo: Optional[CargoEnum] = None
    salario: Optional[float] = None
    multiplex_id: Optional[int] = None

class EmpleadoResponse(BaseModel):
    id: int
    nombre: str
    email: str
    cargo: CargoEnum
    multiplex_id: Optional[int]
    estado: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class EmpleadoDetalle(BaseModel):
    id: int
    primer_nombre: str
    segundo_nombre: Optional[str]
    primer_apellido: str
    segundo_apellido: Optional[str]
    cedula_ciudadania: str
    fecha_nacimiento: date
    telefono: str
    email: str
    cargo: CargoEnum
    salario: float
    multiplex_id: Optional[int]
    correo_laboral: Optional[str]
    estado: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class EmpleadoListElement(BaseModel):
    id: int
    primer_nombre: str
    primer_apellido: str
    cargo: CargoEnum
    multiplex_id: Optional[int]

    model_config = {
        "from_attributes": True
    }

class EmpleadoPaginated(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    data: List[EmpleadoListElement]
