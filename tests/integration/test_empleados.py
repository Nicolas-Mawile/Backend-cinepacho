"""Integration tests for Empleado endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import date

client = TestClient(app)

@pytest.fixture
def test_multiplex(db_session):
    from app.infrastructure.models.multiplex import Multiplex
    m = Multiplex(
        codigo="MUX01",
        nombre="Multiplex Central",
        ciudad="Bogota",
        direccion="Calle 123",
        latitud=4.6,
        longitud=-74.0
    )
    db_session.add(m)
    db_session.commit()
    db_session.refresh(m)
    return m

def test_crear_empleado_exitoso(db_session, test_multiplex):
    payload = {
        "primer_nombre": "Carlos",
        "segundo_nombre": "Arturo",
        "primer_apellido": "Gomez",
        "segundo_apellido": "Perez",
        "cedula_ciudadania": "12345678",
        "fecha_nacimiento": "1990-01-01",
        "telefono": "3001234567",
        "email": "carlos@example.com",
        "cargo": "cajero",
        "salario": 1500000,
        "multiplex_id": test_multiplex.id
    }
    response = client.post("/api/v1/empleados", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Empleado creado correctamente"
    assert data["empleado"]["nombre"] == "Carlos Arturo Gomez Perez"
    assert "email" in data["empleado"]

def test_listar_empleados_paginado(db_session, test_multiplex):
    # Crear un par de empleados
    payload = {
        "primer_nombre": "Emp",
        "primer_apellido": "1",
        "cedula_ciudadania": "1",
        "fecha_nacimiento": "1990-01-01",
        "telefono": "1",
        "email": "1@ex.com",
        "cargo": "aseador",
        "salario": 1000,
        "multiplex_id": test_multiplex.id
    }
    client.post("/api/v1/empleados", json=payload)
    
    response = client.get("/api/v1/empleados?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["data"]) >= 1

def test_obtener_detalle_empleado(db_session, test_multiplex):
    payload = {
        "primer_nombre": "Detalle",
        "primer_apellido": "Test",
        "cedula_ciudadania": "999",
        "fecha_nacimiento": "1990-01-01",
        "telefono": "999",
        "email": "999@ex.com",
        "cargo": "director",
        "salario": 5000,
        "multiplex_id": test_multiplex.id
    }
    create_resp = client.post("/api/v1/empleados", json=payload)
    emp_id = create_resp.json()["empleado"]["id"]
    
    response = client.get(f"/api/v1/empleados/{emp_id}")
    assert response.status_code == 200
    assert response.json()["cedula_ciudadania"] == "999"
    assert "correo_laboral" in response.json()

def test_actualizar_empleado(db_session, test_multiplex):
    payload = {
        "primer_nombre": "Update",
        "primer_apellido": "Me",
        "cedula_ciudadania": "555",
        "fecha_nacimiento": "1990-01-01",
        "telefono": "555",
        "email": "555@ex.com",
        "cargo": "cajero",
        "salario": 1000,
        "multiplex_id": test_multiplex.id
    }
    create_resp = client.post("/api/v1/empleados", json=payload)
    emp_id = create_resp.json()["empleado"]["id"]
    
    update_payload = {
        "cargo": "director",
        "salario": 2000
    }
    response = client.put(f"/api/v1/empleados/{emp_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["empleado"]["cargo"] == "director"
    assert float(response.json()["empleado"]["salario"]) == 2000

def test_deshabilitar_empleado(db_session, test_multiplex):
    payload = {
        "primer_nombre": "Delete",
        "primer_apellido": "Me",
        "cedula_ciudadania": "000",
        "fecha_nacimiento": "1990-01-01",
        "telefono": "000",
        "email": "000@ex.com",
        "cargo": "aseador",
        "salario": 1000,
        "multiplex_id": test_multiplex.id
    }
    create_resp = client.post("/api/v1/empleados", json=payload)
    emp_id = create_resp.json()["empleado"]["id"]
    
    response = client.delete(f"/api/v1/empleados/{emp_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}
    
    # Verificar que está inactivo
    detail = client.get(f"/api/v1/empleados/{emp_id}")
    assert detail.json()["estado"] == "inactivo"
