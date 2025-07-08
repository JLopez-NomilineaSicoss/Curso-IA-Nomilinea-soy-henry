from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_task_not_found_custom():
    response = client.get("/tasks/9999")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "La tarea no fue encontrada"

def test_update_task_not_found_custom():
    response = client.put("/tasks/9999", json={"title": "Nueva"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "La tarea no fue encontrada"

def test_delete_task_not_found_custom():
    # Usar autenticación válida
    from base64 import b64encode
    headers = {
        "Authorization": "Basic " + b64encode(b"admin:admin123").decode()
    }
    response = client.delete("/tasks/9999", headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "La tarea no fue encontrada" 