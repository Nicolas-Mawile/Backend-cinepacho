"""Contrato service — gestión de contratos y cambios de cargo."""
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.infrastructure.models.contrato import Contrato
from app.infrastructure.models.historial_cargo import HistorialCargo
from app.infrastructure.models.cargoEnum import CargoEnum


class ContratoService:
    """
    Gestiona la creación de contratos y el cambio de cargo
    de un empleado dentro de un multiplex.
    """

    def __init__(self, db: Session):
        self.db = db

    def crear_contrato(
        self,
        empleado_id: int,
        multiplex_id: int,
        cargo: CargoEnum,
        salario: float,
        fecha_inicio: date,
    ) -> Contrato:
        # Desactivar contratos anteriores del empleado
        contratos_anteriores = (
            self.db.query(Contrato)
            .filter(Contrato.empleadoId == empleado_id, Contrato.activo == True)
            .all()
        )
        for c in contratos_anteriores:
            c.activo = False

        contrato = Contrato(
            empleadoId=empleado_id,
            multiplexId=multiplex_id,
            cargo=cargo,
            salario=salario,
            fechaInicio=fecha_inicio,
            activo=True,
        )
        self.db.add(contrato)
        self.db.flush()
        self.db.refresh(contrato)
        return contrato

    def cambiar_cargo(
        self,
        empleado_id: int,
        nuevo_cargo: CargoEnum,
        nuevo_salario: float | None = None,
    ) -> Contrato:
        contrato = (
            self.db.query(Contrato)
            .filter(Contrato.empleadoId == empleado_id, Contrato.activo == True)
            .first()
        )
        if not contrato:
            raise HTTPException(
                status_code=404,
                detail="El empleado no tiene contrato activo",
            )

        # Registrar en historial
        historial = HistorialCargo(
            empleadoId=empleado_id,
            cargoAnterior=contrato.cargo,
            cargoNuevo=nuevo_cargo,
            fechaCambio=date.today(),
        )
        self.db.add(historial)

        contrato.cargo = nuevo_cargo
        if nuevo_salario is not None:
            contrato.salario = nuevo_salario

        self.db.flush()
        self.db.refresh(contrato)
        return contrato
