"""Integration tests for the Task Manager API."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# BD en memoria: sin archivos residuales, conexiones compartidas via StaticPool
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


# ─── Health check ─────────────────────────────────────────────────

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ─── Crear tarea ──────────────────────────────────────────────────

def test_create_task():
    response = client.post("/tasks/", json={"title": "Tarea de prueba", "description": "Descripción"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Tarea de prueba"
    assert data["description"] == "Descripción"
    assert data["completed"] is False
    assert "id" in data


def test_create_task_sin_descripcion():
    response = client.post("/tasks/", json={"title": "Solo título"})
    assert response.status_code == 201
    assert response.json()["description"] is None


# ─── Listar tareas ────────────────────────────────────────────────

def test_listar_tareas_vacia():
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []


def test_listar_tareas():
    client.post("/tasks/", json={"title": "Tarea 1"})
    client.post("/tasks/", json={"title": "Tarea 2"})
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 2


# ─── Obtener tarea por ID ─────────────────────────────────────────

def test_get_task_existente():
    created = client.post("/tasks/", json={"title": "Buscar esta"}).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Buscar esta"


def test_get_task_no_existente():
    response = client.get("/tasks/999")
    assert response.status_code == 404


# ─── Actualizar tarea ─────────────────────────────────────────────

def test_update_task():
    created = client.post("/tasks/", json={"title": "Original"}).json()
    response = client.put(f"/tasks/{created['id']}", json={"title": "Actualizada", "completed": True})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Actualizada"
    assert data["completed"] is True


def test_update_task_no_existente():
    response = client.put("/tasks/999", json={"title": "No existe"})
    assert response.status_code == 404


# ─── Eliminar tarea ───────────────────────────────────────────────

def test_eliminar_tarea():
    created = client.post("/tasks/", json={"title": "A eliminar"}).json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 204
    # Verificar que ya no existe
    get_response = client.get(f"/tasks/{created['id']}")
    assert get_response.status_code == 404


def test_eliminar_tarea_no_existente():
    response = client.delete("/tasks/999")
    assert response.status_code == 404
