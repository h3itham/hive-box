# import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "v0.0.1"}


def test_read_temperature():
    response = client.get("/temperature")
    assert response.status_code == 200
    assert "average_temperature" in response.json()
    assert isinstance(response.json()["average_temperature"], float)
