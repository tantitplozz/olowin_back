from fastapi.testclient import TestClient
from ui_server import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    # assert response.json()["status"] == "ok" # Original assertion
    # Updated assertion to match the actual /health response structure
    assert response.json()["api_status"] == "ok"
    assert response.json()["langgraph_compiled"] is True
    # We will check for database_connection == "healthy" separately after DB setup in tests
