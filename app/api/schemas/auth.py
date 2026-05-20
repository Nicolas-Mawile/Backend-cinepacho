from pydantic import BaseModel, EmailStr, Field, field_validator


class RegistroRequest(BaseModel):
    nombres: str = Field(..., min_length=2, max_length=150)
    apellidos: str = Field(..., min_length=2, max_length=150)
    correo: EmailStr
    telefono: str | None
    password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str):
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")

        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe contener al menos una minúscula")

        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")

        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info):

        if ("password" in info.data and v != info.data["password"]):
            raise ValueError("Las contraseñas no coinciden")
        return v


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: dict
