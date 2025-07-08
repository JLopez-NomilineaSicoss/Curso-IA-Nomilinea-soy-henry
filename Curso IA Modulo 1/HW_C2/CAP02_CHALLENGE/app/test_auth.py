from fastapi.testclient import TestClient
from main import app
import base64

client = TestClient(app)

# Credenciales válidas (las que usaremos en la implementación)
USERNAME = "admin"
PASSWORD = "admin123"

# Helper para crear el header de autenticación básica

def basic_auth_header(username, password):
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


def test_delete_all_tasks_no_auth():
    response = client.delete("/tasks/")
    assert response.status_code == 401 or response.status_code == 403

def test_delete_all_tasks_with_invalid_auth():
    headers = basic_auth_header("wrong", "wrong")
    response = client.delete("/tasks/", headers=headers)
    assert response.status_code == 401 or response.status_code == 403

def test_delete_all_tasks_with_valid_auth():
    headers = basic_auth_header(USERNAME, PASSWORD)
    response = client.delete("/tasks/", headers=headers)
    # Puede ser 200 si hay tareas, o 200 aunque no haya tareas
    assert response.status_code == 200
    assert "All tasks deleted" in response.text


def test_delete_task_no_auth():
    response = client.delete("/tasks/1")
    assert response.status_code == 401 or response.status_code == 403

def test_delete_task_with_valid_auth():
    # Primero creamos una tarea
    client.post("/tasks/", json={"title": "Tarea para borrar"})
    headers = basic_auth_header(USERNAME, PASSWORD)
    response = client.delete("/tasks/1", headers=headers)
    assert response.status_code == 200
    assert "Task deleted successfully" in response.text 