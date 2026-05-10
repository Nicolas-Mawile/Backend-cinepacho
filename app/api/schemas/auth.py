from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime

class RegistroRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150)
    correo: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe contener al menos una minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Las contraseñas no coinciden")
        return v

class ClienteResponse(BaseModel):
    id: int
    nombre_completo: str
    correo: EmailStr
    fecha_registro: datetime
    puntos_acumulados: int
    idioma_preferido: str

    model_config = {
        "from_attributes": True
    }

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    cliente: ClienteResponse
