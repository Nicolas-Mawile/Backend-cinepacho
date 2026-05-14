"""Empleado repository."""

from sqlalchemy import select, func
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.cargoEnum import CargoEnum
from ..base_repository import AbstractRepository


class EmpleadoRepository(AbstractRepository[Empleado]):
    """Repositorio para la entidad Empleado."""

    def crear(self, empleado: Empleado) -> Empleado:
        """Agrega un nuevo empleado."""
        self.db.add(empleado)
        self.db.commit()
        self.db.refresh(empleado)
        return empleado

    def add(self, entity: Empleado) -> Empleado:
        """Alias para crear, cumpliendo con AbstractRepository."""
        return self.crear(entity)

    def buscar_por_id(self, entity_id: int) -> Empleado | None:
        """Obtiene un empleado por ID."""
        stmt = select(Empleado).where(Empleado.id == entity_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get(self, entity_id: int) -> Empleado | None:
        """Alias para buscar_por_id."""
        return self.buscar_por_id(entity_id)

    def listar(self, multiplex_id: int | None = None, cargo: CargoEnum | None = None, activo: bool | None = None, pagina: int = 1, limite: int = 10) -> list[Empleado]:
        """Lista empleados con paginación y filtros."""
        skip = (pagina - 1) * limite
        stmt = select(Empleado)
        
        if multiplex_id is not None:
            stmt = stmt.where(Empleado.multiplex_id == multiplex_id)
        if cargo is not None:
            stmt = stmt.where(Empleado.cargo == cargo)
        if activo is not None:
            stmt = stmt.where(Empleado.activo == activo)
        
        stmt = stmt.offset(skip).limit(limite)
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_all(self, skip: int = 0, limit: int = 10) -> list[Empleado]:
        """Alias para listar usando skip/limit."""
        pagina = (skip // limit) + 1
        return self.listar(pagina=pagina, limite=limit)

    def count(self, multiplex_id: int | None = None, cargo: CargoEnum | None = None, activo: bool | None = None) -> int:
        """Cuenta el total de empleados con filtros."""
        stmt = select(func.count(Empleado.id))
        if multiplex_id is not None:
            stmt = stmt.where(Empleado.multiplex_id == multiplex_id)
        if cargo is not None:
            stmt = stmt.where(Empleado.cargo == cargo)
        if activo is not None:
            stmt = stmt.where(Empleado.activo == activo)
        return self.db.scalar(stmt) or 0

    def actualizar(self, entity_id: int, updates: dict) -> Empleado | None:
        """Actualiza un empleado."""
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
        """Alias para actualizar."""
        return self.actualizar(entity_id, updates)

    def desactivar(self, entity_id: int) -> bool:
        """Deshabilita un empleado (soft delete)."""
        entity = self.buscar_por_id(entity_id)
        if not entity:
            return False
        
        entity.activo = False
        self.db.commit()
        return True

    def delete(self, entity_id: int) -> bool:
        """Alias para desactivar."""
        return self.desactivar(entity_id)

    def exists(self, entity_id: int) -> bool:
        """Verifica existencia por ID."""
        stmt = select(func.count()).where(Empleado.id == entity_id)
        result = self.db.scalar(stmt)
        return result > 0

    def buscar_por_cedula(self, cedula: str) -> Empleado | None:
        """Busca un empleado por su cédula."""
        stmt = select(Empleado).where(Empleado.cedula == cedula)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def buscar_por_codigo(self, codigo: str) -> Empleado | None:
        """Busca un empleado por su código."""
        stmt = select(Empleado).where(Empleado.codigo_empleado == codigo)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def siguiente_numero_secuencia(self, multiplex_codigo: str) -> int:
        """Obtiene el siguiente número secuencial usando MAX(seq)+1.
        Bloquea el multiplex para evitar colisiones en la secuencia.
        """
        prefijo = f"CP-{multiplex_codigo}-"
        stmt = (select(Empleado.codigoEmpleado)
                .where(Empleado.codigoEmpleado.like(f"{prefijo}%")).order_by(Empleado.id.desc()).limit(1))
        ultimoCodigo = self.db.execute(stmt).scalar()

        if not ultimoCodigo:
            return 1

        try:
            numero = int(ultimoCodigo.split("-")[-1])
            return numero + 1

        except Exception:
            return 1

    def obtener_ultimo_secuencial(self, multiplex_id: int) -> int:
        """Obtiene el último número secuencial (sin lock)."""
        stmt = select(func.max(Empleado.seq)).where(Empleado.multiplex_id == multiplex_id)
        max_seq = self.db.execute(stmt).scalar()
        return max_seq or 0

    def tiene_acceso_sistema(self, cargo: CargoEnum) -> bool:
        """Verifica si el cargo tiene acceso al sistema."""
        cargos_con_acceso = [
            CargoEnum.cajero,
            CargoEnum.administrador, # admin_multiplex / admin_general
            CargoEnum.director       # director
        ]
        return cargo in cargos_con_acceso

    def buscarPorCorreo(self, correo: str) -> Empleado | None:
        stmt = select(Empleado).where(Empleado.correo == correo)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def buscarPorCorreoLaboral(self, correoLaboral: str) -> Empleado | None:
        stmt = select(Empleado).where(Empleado.correoLaboral == correoLaboral)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def cambiarEstado(self, entity_id: int, activo: bool) -> Empleado | None:
        empleado = self.buscar_por_id(entity_id)
        if not empleado:
            return None
        
        empleado.activo = activo
        self.db.commit()
        self.db.refresh(empleado)
        return empleado