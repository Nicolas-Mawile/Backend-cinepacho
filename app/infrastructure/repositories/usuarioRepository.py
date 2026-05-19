from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.cliente import Cliente

class UsuarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def crear(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def buscarPorId(self, id: int) -> Usuario:
        stmt = select(Usuario).where(Usuario.id == id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def buscarPorCorreo(self, correo: str):
        stmtEmpleado = (
            select(Usuario)
            .join(Empleado, Usuario.empleadoId == Empleado.id)
            .where(Empleado.correoLaboral == correo)
        )

        usuarioEmpleado = (self.db.execute(stmtEmpleado)).scalar_one_or_none()
        
        if usuarioEmpleado:
            return usuarioEmpleado
        
        stmtCliente = (select(Usuario).join(Cliente, Usuario.clienteId == Cliente.id).where(Cliente.correo == correo))
        
        return (self.db.execute(stmtCliente)).scalar_one_or_none()
