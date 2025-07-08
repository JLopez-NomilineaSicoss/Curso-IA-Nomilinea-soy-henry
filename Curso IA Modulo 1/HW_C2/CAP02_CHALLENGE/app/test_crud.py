from fastapi.testclient import TestClient
from app.main import app
import base64

client = TestClient(app)

def basic_auth_header(username, password):
    credentials = f"{username}:{password}"
    import base64 as b64
    encoded = b64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}

USERNAME = "admin"
PASSWORD = "admin123"

def test_create_task():
    response = client.post("/tasks/", json={"title": "Tarea CRUD", "description": "desc"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Tarea CRUD"
    assert data["description"] == "desc"
    assert data["completed"] is False

def test_list_tasks():
    # Crear dos tareas para asegurar que la lista no esté vacía
    client.post("/tasks/", json={"title": "Tarea 1"})
    client.post("/tasks/", json={"title": "Tarea 2"})
    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert isinstance(data["tasks"], list)
    assert len(data["tasks"]) >= 2

def test_update_task():
    # Crear una tarea
    client.post("/tasks/", json={"title": "Actualizar"})
    # Actualizar la tarea con ID 1
    response = client.put("/tasks/1", json={"title": "Actualizada", "completed": True})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Actualizada"
    assert data["completed"] is True 