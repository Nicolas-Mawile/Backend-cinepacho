from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.persona import Persona
from app.infrastructure.models.empleado import Empleado


class UsuarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def buscarPorCorreo(self, correo: str):

        if correo.endswith("@cinepacho.com"):
            stmt = (
                select(Usuario)
                .join(Persona)
                .join(Empleado, Empleado.id == Persona.id)
                .where(Empleado.correoLaboral == correo)
            )

        else:
            stmt = (
                select(Usuario)
                .join(Persona)
                .where(Persona.correo == correo)
            )

        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def crear(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def buscarPorId(self, id: int) -> Usuario:
        stmt = select(Usuario).where(Usuario.id == id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()