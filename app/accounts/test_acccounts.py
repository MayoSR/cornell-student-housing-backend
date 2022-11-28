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

    # Delete everything in database
    response: Response = client.delete("/api/")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    
    # Transfer control to a test
    yield

    # Clear everything in database
    response: Response = client.delete("/api/")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

def test_create_account():

    # Make first account
    response: Response = client.post(
        "/api/accounts/",
        json={
            "fname": "Maheer",
            "lname": "Aeron",
            "email": "maa368@cornell.edu"
        }
    )
    assert response.status_code == 200

    # Now call get on all accounts
    response = client.get("/api/accounts/")
    print(response.json())