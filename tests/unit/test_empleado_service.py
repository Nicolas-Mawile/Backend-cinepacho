from sqlalchemy import select

from app.domain.services.empleado_service import EmpleadoService
from app.infrastructure.models.cliente import Cliente
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.multiplex import Multiplex
from app.infrastructure.models.rol import Rol
from app.infrastructure.models.usuario import Usuario
from app.infrastructure.models.cargoEnum import CargoEnum
from app.infrastructure.repositories.empleado_repository import EmpleadoRepository


def _crear_roles(db_session):
    db_session.add(Rol(nombre="CLIENTE"))
    db_session.add(Rol(nombre="EMPLEADO-CAJERO"))
    db_session.commit()


def _crear_multiplex(db_session):
    multiplex = Multiplex(
        codigo="MUX01",
        nombre="Multiplex Central",
        ciudad="Bogota",
        direccion="Calle 123",
        latitud=4.6,
        longitud=-74.0,
    )
    db_session.add(multiplex)
    db_session.commit()
    db_session.refresh(multiplex)
    return multiplex


def test_crear_empleado_tambien_crea_usuario_cliente(db_session):
    _crear_roles(db_session)
    multiplex = _crear_multiplex(db_session)

    service = EmpleadoService(db_session)
    repo = EmpleadoRepository(db_session)
    datos = {
        "nombres": "Carlos",
        "apellidos": "Gomez",
        "correo": "carlos@example.com",
        "telefono": "3001234567",
        "password": "Password123",
        "cargo": CargoEnum.cajero,
        "salario": 1500000,
        "multiplexId": multiplex.id,
    }

    resultado = service.crearEmpleado(repo, datos)

    assert resultado["credenciales"]["correo"] == "carlos.gomez@cinepacho.com"
    assert resultado["credencialesCliente"]["correo"] == "carlos@example.com"

    empleado = db_session.execute(select(Empleado).where(Empleado.correoLaboral == "carlos.gomez@cinepacho.com")).scalar_one()
    cliente = db_session.execute(select(Cliente).where(Cliente.correo == "carlos@example.com")).scalar_one()

    usuario_empleado = db_session.execute(select(Usuario).where(Usuario.personaId == empleado.id)).scalar_one()
    usuario_cliente = db_session.execute(select(Usuario).where(Usuario.personaId == cliente.id)).scalar_one()

    assert empleado.usuarioId == usuario_empleado.id
    assert cliente.usuarioId == usuario_cliente.id
    assert usuario_empleado.rol.nombre == "EMPLEADO-CAJERO"
    assert usuario_cliente.rol.nombre == "CLIENTE"