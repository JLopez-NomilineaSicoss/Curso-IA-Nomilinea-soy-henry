import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Pruebas para validación de creación de tareas

def test_create_task_valid():
    response = client.post("/tasks/", json={"title": "Tarea válida", "description": "Descripción", "completed": False})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Tarea válida"
    assert data["completed"] is False

def test_create_task_missing_title():
    response = client.post("/tasks/", json={"description": "Sin título"})
    assert response.status_code == 422  # Unprocessable Entity

def test_create_task_invalid_completed_type():
    response = client.post("/tasks/", json={"title": "Tarea", "completed": "no es bool"})
    assert response.status_code == 422

# Pruebas para validación de obtención de tarea por ID

def test_get_task_invalid_id():
    response = client.get("/tasks/abc")
    assert response.status_code == 422

def test_get_task_not_found():
    response = client.get("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found" 