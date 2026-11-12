"""
conftest.py — Fixtures globales de pytest para Unified Service Desk.

Proporciona:
- Base de datos en memoria aislada por sesión de prueba.
- TestClient de FastAPI configurado.
- Usuarios sembrados con contraseñas hasheadas.
- Tokens JWT válidos e inválidos para pruebas de seguridad.
"""

import os
import sys
import pytest

# Garantizar que el módulo raíz del proyecto esté en PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from backend.core.database import DatabaseManager


@pytest.fixture(scope="session")
def db():
    """
    Base de datos SQLite en memoria aislada para toda la sesión de prueba.
    Se reinicia el Singleton antes de crear la instancia de test.
    """
    DatabaseManager.reset_instance_for_testing()
    database = DatabaseManager("sqlite:///:memory:")
    database.create_all_tables()
    return database


@pytest.fixture(scope="session")
def client(db):
    """
    TestClient de FastAPI con base de datos en memoria.
    La importación de la app ocurre DESPUÉS de reiniciar el Singleton.
    """
    from backend.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def seeded_users(client):
    """
    Retorna el diccionario de usuarios sembrados indexados por rol.
    Se usa como fixture de base para todos los tests.
    """
    res = client.get("/api/v1/users/")
    assert res.status_code == 200, f"No se pudieron obtener usuarios: {res.text}"
    users = res.json()
    assert len(users) >= 5, f"Se esperaban al menos 5 usuarios, se encontraron {len(users)}"

    by_role = {}
    for u in users:
        by_role[u["role"]] = u

    assert "STUDENT" in by_role, "No se encontró usuario STUDENT"
    assert "STAFF" in by_role, "No se encontró usuario STAFF"
    assert "IT_STUDENT_SUPPORT" in by_role, "No se encontró usuario IT_STUDENT_SUPPORT"
    assert "IT_STAFF_SUPPORT" in by_role, "No se encontró usuario IT_STAFF_SUPPORT"
    assert "ADMIN" in by_role, "No se encontró usuario ADMIN"

    return by_role


@pytest.fixture(scope="session")
def demo_password():
    """Contraseña de los usuarios de prueba (desde settings)."""
    from backend.core.config import settings
    return settings.SEED_DEFAULT_PASSWORD


@pytest.fixture(scope="session")
def admin_token(client, seeded_users, demo_password):
    """JWT de ADMIN para pruebas que requieren permisos elevados."""
    admin = seeded_users["ADMIN"]
    res = client.post("/api/v1/users/login", json={"email": admin["email"], "password": demo_password})
    assert res.status_code == 200, f"Login ADMIN falló: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="session")
def student_token(client, seeded_users, demo_password):
    """JWT de STUDENT para pruebas de aislamiento de datos."""
    student = seeded_users["STUDENT"]
    res = client.post("/api/v1/users/login", json={"email": student["email"], "password": demo_password})
    assert res.status_code == 200, f"Login STUDENT falló: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="session")
def it_student_token(client, seeded_users, demo_password):
    """JWT de IT_STUDENT_SUPPORT para pruebas de asignación."""
    it_user = seeded_users["IT_STUDENT_SUPPORT"]
    res = client.post("/api/v1/users/login", json={"email": it_user["email"], "password": demo_password})
    assert res.status_code == 200, f"Login IT_STUDENT_SUPPORT falló: {res.text}"
    return res.json()["access_token"]


def auth_headers(token: str) -> dict:
    """Helper para construir headers de autorización Bearer."""
    return {"Authorization": f"Bearer {token}"}
