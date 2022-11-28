"""
Test file for accounts route
"""

# Pytest imports
import pytest

# FastAPI imports
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

# Main app import
from ..main import app

# Model imports
from .models import Account
from ..properties.models import Property
from ..property_images.models import PropertyImage
from ..reviews.models import Review

# Create new client
client: TestClient = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    pass

def test_get_home():
    response: Response = client.get("/api")
    assert response.status_code == 200