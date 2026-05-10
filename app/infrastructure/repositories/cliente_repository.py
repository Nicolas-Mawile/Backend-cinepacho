"""Cliente repository."""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.infrastructure.base_repository import AbstractRepository
from app.models.cliente import Cliente


class ClienteRepository(AbstractRepository[Cliente]):
    def __init__(self, db: Session):
        self.db = db

    def add(self, entity: Cliente) -> Cliente:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get(self, entity_id: int) -> Cliente | None:
        return self.db.get(Cliente, entity_id)

    def get_all(self, skip: int = 0, limit: int = 10) -> list[Cliente]:
        result = self.db.execute(select(Cliente).offset(skip).limit(limit))
        return list(result.scalars().all())

    def update(self, entity_id: int, data: dict) -> Cliente | None:
        entity = self.get(entity_id)
        if not entity:
            return None
        for key, value in data.items():
            setattr(entity, key, value)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity_id: int) -> bool:
        entity = self.get(entity_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True

    def exists(self, entity_id: int) -> bool:
        return self.get(entity_id) is not None

    def crear(self, datos_cliente: dict) -> Cliente:
        return self.add(Cliente(**datos_cliente))

    def buscar_por_correo(self, correo: str) -> Cliente | None:
        result = self.db.execute(select(Cliente).where(Cliente.correo == correo))
        return result.scalar_one_or_none()

    def buscar_por_id(self, id: int) -> Cliente | None:
        return self.get(id)

    def existe_correo(self, correo: str) -> bool:
        return self.buscar_por_correo(correo) is not None

    def actualizar_puntos(self, entity_id: int, delta_puntos: int) -> Cliente:
        cliente = self.get(entity_id)
        if not cliente:
            raise ValueError(f"Cliente con id {entity_id} no existe")
        cliente.puntos = (cliente.puntos or 0) + delta_puntos
        self.db.commit()
        self.db.refresh(cliente)
        return cliente

    def registrar_intento_fallido(self, correo: str) -> None:
        cliente = self.buscar_por_correo(correo)
        if not cliente:
            return
        cliente.intentos_fallidos = (cliente.intentos_fallidos or 0) + 1
        cliente.ultimo_intento = datetime.now(timezone.utc)
        self.db.commit()

    def reset_intentos(self, correo: str) -> None:
        cliente = self.buscar_por_correo(correo)
        if not cliente:
            return
        cliente.intentos_fallidos = 0
        cliente.ultimo_intento = None
        cliente.ultimo_login = datetime.now(timezone.utc)
        self.db.commit()

    def verificar_bloqueo(self, correo: str) -> bool:
        cliente = self.buscar_por_correo(correo)
        if not cliente:
            return False
        if cliente.intentos_fallidos >= 5 and cliente.ultimo_intento:
            ultimo = cliente.ultimo_intento
            if ultimo.tzinfo is None:
                ultimo = ultimo.replace(tzinfo=timezone.utc)
            return datetime.now(timezone.utc) - ultimo < timedelta(minutes=15)
        return False