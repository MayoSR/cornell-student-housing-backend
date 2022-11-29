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


### TEST HTTP GET FUNCTIONS ###

def test_get_all_accounts():
    
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

    # Make second account
    response = client.post(
        "/api/accounts/",
        json={
            "fname": "Mayank",
            "lname": "Rao",
            "email": "ms3293@cornell.edu"
        }
    )
    assert response.status_code == 200

    # Make third account
    response = client.post(
        "/api/accounts/",
        json={
            "fname": "Brett",
            "lname": "Schelsinger",
            "email": "bgs59@cornell.edu"
        }
    )
    assert response.status_code == 200

    # Now call get on all accounts
    response = client.get("/api/accounts/")

    # Check length of accounts
    accounts: list = response.json()
    assert len(accounts) == 3

def test_get_account():

    # Make account
    response: Response = client.post(
        "/api/accounts/",
        json={
            "fname": "Maheer",
            "lname": "Aeron",
            "email": "maa368@cornell.edu"
        }
    )
    assert response.status_code == 200

    # Now call get on account by id
    created_acc: dict = response.json()
    response = client.get(f"/api/accounts/{created_acc['id']}")

    # Check against returned account
    getted_acc: dict = response.json()

    # Check account properties itself
    assert getted_acc["id"] == created_acc["id"]
    assert getted_acc["fname"] == created_acc["fname"]
    assert getted_acc["lname"] == created_acc["lname"]
    assert getted_acc["email"] == created_acc["email"]
    assert getted_acc["created"] == created_acc["created"]

### TEST HTTP POST FUNCTIONS ###

def test_create_account():
    """
    Tests for creating an account
    """

    # Make account
    response: Response = client.post(
        "/api/accounts/",
        json={
            "fname": "Maheer",
            "lname": "Aeron",
            "email": "maa368@cornell.edu"
        }
    )
    assert response.status_code == 200

    # Extract account from json
    account: dict = response.json()
    assert account["fname"] == "Maheer"
    assert account["lname"] == "Aeron"
    assert account["email"] == "maa368@cornell.edu"

### TEST HTTP PATCH FUNCTIONS ###

def test_update_account():

    # Make account
    response: Response = client.post(
        "/api/accounts/",
        json={
            "fname": "Maheer",
            "lname": "Aeron",
            "email": "maa368@cornell.edu"
        }
    )
    assert response.status_code == 200

    # Extract account from json
    acc_json: dict = response.json()
    
    # Try updating account
    response = client.patch(
        f"/api/accounts/{acc_json['id']}",
        json={
            "fname": "Mahee",
            "lname": "Aero",
            "email": "maa368@cornell.ed"
        }
    )
    assert response.status_code == 200

    # Now issue a get and test the fields
    response = client.get(f"/api/accounts/{acc_json['id']}")
    mod_acc_json: dict = response.json()

    assert mod_acc_json["fname"] == "Mahee"
    assert mod_acc_json["lname"] == "Aero"
    assert mod_acc_json["email"] == "maa368@cornell.ed"

### TEST HTTP DELETE FUNCTIONS ###

def test_delete_account():

    # Make account
    response: Response = client.post(
        "/api/accounts/",
        json={
            "fname": "Maheer",
            "lname": "Aeron",
            "email": "maa368@cornell.edu"
        }
    )
    assert response.status_code == 200

    # Extract account from json
    acc_json: dict = response.json()

    # Delete account
    response = client.delete(f"/api/accounts/{acc_json['id']}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # Try get on all accounts and ensure it really deleted
    response = client.get("/api/accounts/")
    assert response.status_code == 200
    assert len(response.json()) == 0