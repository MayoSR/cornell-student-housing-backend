"""
Test file for home route
"""

# FastAPI imports
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

# Main app import
from ..main import app

# Create new client
client: TestClient = TestClient(app)

def test_get_home():
    response: Response = client.get("/api")
    assert response.status_code == 200