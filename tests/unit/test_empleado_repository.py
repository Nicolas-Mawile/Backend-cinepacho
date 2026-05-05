import pytest
from datetime import date
from decimal import Decimal
from app.infrastructure.models.empleado import Empleado
from app.infrastructure.models.cargoEnum import CargoEnum
from app.infrastructure.repositories.empleado_repository import EmpleadoRepository

@pytest.fixture
def repo(db_session):
    """Instancia del repositorio."""
    return EmpleadoRepository(db_session)

def empleado_data(**kwargs):
    """Factory para crear datos de Empleado."""
    cedula = kwargs.get("cedula", "123456789")
    defaults = {
        "nombre": "Juan",
        "apellido": "Perez",
        "cedula": cedula,
        "nombre_completo": "Juan Perez",
        "codigo_empleado": f"CP-TIT-{cedula}",
        "fecha_inicio_contrato": date(2023, 1, 1),
        "salario": Decimal("1000000.00"),
        "cargo": CargoEnum.cajero,
        "multiplex_id": 1,
        "seq": 1,
        "activo": True
    }
    return Empleado(**{**defaults, **kwargs})

def test_crear_empleado(repo):
    """Test creación de empleado."""
    emp = empleado_data()
    creado = repo.crear(emp)
    assert creado.id is not None
    assert creado.nombre == "Juan"
    assert creado.seq == 1

def test_buscar_por_id(repo):
    """Test buscar empleado por ID."""
    emp = repo.crear(empleado_data())
    buscado = repo.buscar_por_id(emp.id)
    assert buscado is not None
    assert buscado.id == emp.id

def test_buscar_por_cedula(repo):
    """Test buscar empleado por cédula."""
    repo.crear(empleado_data(cedula="987654321"))
    buscado = repo.buscar_por_cedula("987654321")
    assert buscado is not None
    assert buscado.cedula == "987654321"

def test_buscar_por_codigo(repo):
    """Test buscar empleado por código."""
    repo.crear(empleado_data(codigo_empleado="CP-TIT-9999"))
    buscado = repo.buscar_por_codigo("CP-TIT-9999")
    assert buscado is not None
    assert buscado.codigo_empleado == "CP-TIT-9999"

def test_listar_con_filtros(repo):
    """Test listar empleados con filtros y paginación."""
    repo.crear(empleado_data(cedula="1", multiplex_id=1, cargo=CargoEnum.cajero))
    repo.crear(empleado_data(cedula="2", multiplex_id=1, cargo=CargoEnum.aseador))
    repo.crear(empleado_data(cedula="3", multiplex_id=2, cargo=CargoEnum.cajero))
    
    # Filtro por multiplex
    result = repo.listar(multiplex_id=1)
    assert len(result) == 2
    
    # Filtro por cargo
    result = repo.listar(cargo=CargoEnum.cajero)
    assert len(result) == 2
    
    # Filtro por multiplex y cargo
    result = repo.listar(multiplex_id=1, cargo=CargoEnum.cajero)
    assert len(result) == 1
    
    # Paginación
    result = repo.listar(pagina=1, limite=2)
    assert len(result) == 2
    result = repo.listar(pagina=2, limite=2)
    assert len(result) == 1

def test_siguiente_numero_secuencia(repo):
    """Test generación de siguiente número secuencial."""
    # Inicialmente debe ser 1
    assert repo.siguiente_numero_secuencia(1) == 1
    
    # Crear uno con seq=1
    repo.crear(empleado_data(cedula="10", multiplex_id=1, seq=1))
    assert repo.siguiente_numero_secuencia(1) == 2
    
    # Crear uno con seq=5
    repo.crear(empleado_data(cedula="11", multiplex_id=1, seq=5))
    assert repo.siguiente_numero_secuencia(1) == 6
    
    # Multiplex diferente
    assert repo.siguiente_numero_secuencia(2) == 1

def test_actualizar_empleado(repo):
    """Test actualizar datos de empleado."""
    emp = repo.crear(empleado_data())
    updates = {"salario": Decimal("1500000.00"), "cargo": CargoEnum.director}
    actualizado = repo.actualizar(emp.id, updates)
    assert actualizado.salario == Decimal("1500000.00")
    assert actualizado.cargo == CargoEnum.director

def test_desactivar_empleado(repo):
    """Test desactivar empleado."""
    emp = repo.crear(empleado_data())
    repo.desactivar(emp.id)
    buscado = repo.buscar_por_id(emp.id)
    assert buscado.activo is False

def test_tiene_acceso_sistema(repo):
    """Test lógica de permisos por cargo."""
    assert repo.tiene_acceso_sistema(CargoEnum.cajero) is True
    assert repo.tiene_acceso_sistema(CargoEnum.administrador) is True
    assert repo.tiene_acceso_sistema(CargoEnum.director) is True
    assert repo.tiene_acceso_sistema(CargoEnum.aseador) is False
    assert repo.tiene_acceso_sistema(CargoEnum.despachador_comida) is False
