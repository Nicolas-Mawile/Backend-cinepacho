"""Empleado repository."""
from sqlalchemy import (select, func)
from sqlalchemy.orm import joinedload
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.contrato import Contrato
from app.infrastructure.models.cargoEnum import CargoEnum
from ..base_repository import AbstractRepository

class EmpleadoRepository(AbstractRepository[Empleado]):
    """
    Repositorio empleados.
    """
    # ==========================================
    # CREAR
    # ==========================================

    def crear(self,empleado: Empleado) -> Empleado:
        self.db.add(empleado)
        self.db.commit()
        self.db.refresh(empleado)
        return empleado

    def add(self, entity: Empleado) -> Empleado:
        return self.crear(entity)

    # ==========================================
    # BUSCAR POR ID
    # ==========================================
    def buscar_por_id(self, entity_id: int) -> Empleado | None:
        stmt = (select(Empleado).options(joinedload(Empleado.cliente),joinedload(Empleado.contratos)).where(Empleado.id == entity_id))
        result = self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    def get(self, entity_id: int) -> Empleado | None:
        return self.buscar_por_id(entity_id)

    # ==========================================
    # LISTAR
    # ==========================================
    def listar(self, multiplex_id: int | None = None, cargo: CargoEnum | None = None, 
               activo: bool | None = None, pagina: int = 1, limite: int = 10) -> list[Empleado]:
        skip = (pagina - 1) * limite
        stmt = (select(Empleado).options(joinedload(Empleado.cliente),joinedload(Empleado.contratos)))

        # ======================================
        # FILTRO ACTIVO
        # ======================================
        if activo is not None:
            stmt = stmt.where(Empleado.activo == activo)
        empleados = (self.db.execute(stmt).scalars().unique().all())

        # ======================================
        # FILTRO MULTIPLEX
        # ======================================
        if multiplex_id is not None:
            empleados = [empleado for empleado in empleados 
                         if (empleado.contratoActivo and empleado.contratoActivo.multiplexId == multiplex_id)]

        # ======================================
        # FILTRO CARGO
        # ======================================
        if cargo is not None:
            empleados = [empleado for empleado in empleados if (empleado.cargoActual == cargo)]

        return empleados[skip: skip + limite]

    # ==========================================
    # TOTAL
    # ==========================================
    def count(self, activo: bool | None = None) -> int:
        stmt = select(func.count(Empleado.id))
        if activo is not None:
            stmt = stmt.where(Empleado.activo == activo)

        return self.db.scalar(stmt) or 0

    # ==========================================
    # ACTUALIZAR
    # ==========================================
    def actualizar(self, entity_id: int, updates: dict) -> Empleado | None:
        entity = self.buscar_por_id(entity_id)
        if not entity:
            return None

        for key, value in updates.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity_id: int, updates: dict) -> Empleado | None:
        return self.actualizar(entity_id, updates)

    # ==========================================
    # CAMBIAR ESTADO
    # ==========================================

    def cambiarEstado(self, entity_id: int, activo: bool) -> Empleado | None:
        empleado = self.buscar_por_id(entity_id)
        if not empleado:
            return None

        empleado.activo = activo
        self.db.commit()
        self.db.refresh(empleado)
        return empleado

    # ==========================================
    # DELETE
    # ==========================================
    def desactivar(self, entity_id: int) -> bool:
        empleado = self.buscar_por_id(entity_id)
        if not empleado:
            return False
        empleado.activo = False
        self.db.commit()
        return True

    def delete(self, entity_id: int) -> bool:
        return self.desactivar(entity_id)

    # ==========================================
    # EXISTS
    # ==========================================
    def exists(self, entity_id: int) -> bool:
        stmt = (select(func.count()).where(Empleado.id == entity_id))
        result = self.db.scalar(stmt)
        return result > 0

    # ==========================================
    # BUSCAR POR CORREO PERSONAL
    # ==========================================
    def buscarPorCorreo(self, correo: str) -> Empleado | None:
        stmt = (select(Empleado).where(Empleado.correo == correo))
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ==========================================
    # BUSCAR POR CORREO LABORAL
    # ==========================================
    def buscarPorCorreoLaboral(self, correo: str) -> Empleado | None:
        stmt = (select(Empleado).where(Empleado.correoLaboral == correo))
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ==========================================
    # BUSCAR POR CÓDIGO
    # ==========================================
    def buscarPorCodigo(self, codigo: str) -> Empleado | None:
        stmt = (select(Empleado).where(Empleado.codigoEmpleado == codigo))
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ==========================================
    # SECUENCIA EMPLEADO
    # ==========================================
    def siguiente_numero_secuencia(self, multiplex_codigo: str) -> int:
        prefijo = (f"CP-{multiplex_codigo}-")
        stmt = (select(Empleado.codigoEmpleado).where(Empleado.codigoEmpleado.like(f"{prefijo}%"))
                .order_by(Empleado.id.desc()).limit(1))

        ultimoCodigo = (self.db.execute(stmt).scalar())
        if not ultimoCodigo:
            return 1
        try:
            numero = int(ultimoCodigo.split("-")[-1])
            return numero + 1
        except Exception:
            return 1
        

    def get_all(self) -> list[Empleado]:
        stmt = select(Empleado)
        result = self.db.execute(stmt)
        return result.scalars().all()