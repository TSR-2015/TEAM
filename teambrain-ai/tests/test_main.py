from fastapi.testclient import TestClient
import sys
import os

# Ensure the app folder is in the python path for testing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "documentation" in response.json()

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "TeamBrain AI"}
