from sqlalchemy import select

from sqlalchemy.orm import Session

from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.persona import Persona
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.cliente import Cliente


class UsuarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def buscarPorCorreo(self, correo: str):
        stmt = (
            select(Usuario)
            .join(Empleado, Usuario.personaId == Empleado.id)
            .where(Empleado.correoLaboral == correo)
            .limit(1)
        )

        result = self.db.execute(stmt)
        usuario = result.scalars().first()
        if usuario:
            return usuario

        stmt = (
            select(Usuario)
            .join(Cliente, Usuario.personaId == Cliente.id)
            .where(Cliente.correo == correo)
            .limit(1)
        )

        result = self.db.execute(stmt)
        usuario = result.scalars().first()
        if usuario:
            return usuario

        stmt = (
            select(Usuario)
            .join(Persona, Usuario.personaId == Persona.id)
            .where(Persona.correo == correo)
            .limit(1)
        )

        result = self.db.execute(stmt)
        return result.scalars().first()

    def crear(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def buscarPorId(self, id: int) -> Usuario:
        stmt = select(Usuario).where(Usuario.id == id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def buscarPorCorreoLogin(self, correo: str) -> Usuario | None:
        return self.buscarPorCorreo(correo)
    