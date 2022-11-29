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
from ..accounts.models import Account
from ..properties.models import Property
from ..property_images.models import PropertyImage
from ..reviews.models import Review

# Create new client
client: TestClient = TestClient(app)

class TestAccounts:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):

        # Delete everything in database
        response: Response = client.delete("/api/")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Create a new global account and save it
        response = client.post(
            "/api/accounts/",
            json={
                "fname": "Maheer",
                "lname": "Aeron",
                "email": "maa368@cornell.edu"
            }
        )
        assert response.status_code == 200
        self.me = response.json()
        
        # Transfer control to a test
        yield

        # Clear everything in database
        response: Response = client.delete("/api/")
        assert response.status_code == 200
        assert response.json() == {"ok": True}


    ### TEST HTTP GET FUNCTIONS ###

    def test_get_all_accounts(self):
    
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

    def test_get_account(self):

        # Call get on me and store the fetched acc
        response = client.get(f"/api/accounts/{self.me['id']}")
        fetched_account: dict = response.json()

        # Check account properties itself
        assert fetched_account["id"] == self.me["id"]
        assert fetched_account["fname"] == self.me["fname"]
        assert fetched_account["lname"] == self.me["lname"]
        assert fetched_account["email"] == self.me["email"]
        assert fetched_account["created"] == self.me["created"]

    ### TEST HTTP POST FUNCTIONS ###

    def test_create_account(self):
        """
        Tests for creating an account
        """

        # Setup already creates an account. Just check it
        assert self.me["fname"] == "Maheer"
        assert self.me["lname"] == "Aeron"
        assert self.me["email"] == "maa368@cornell.edu"

    ### TEST HTTP PATCH FUNCTIONS ###

    def test_update_account(self):

        # Try updating account
        response = client.patch(
            f"/api/accounts/{self.me['id']}",
            json={
                "fname": "Mahee",
                "lname": "Aero",
                "email": "maa368@cornell.ed"
            }
        )
        assert response.status_code == 200

        # Now issue a get and test the fields
        response = client.get(f"/api/accounts/{self.me['id']}")
        fetched_account: dict = response.json()

        assert fetched_account["fname"] == "Mahee"
        assert fetched_account["lname"] == "Aero"
        assert fetched_account["email"] == "maa368@cornell.ed"

    ### TEST HTTP DELETE FUNCTIONS ###

    def test_delete_account(self):

        # Delete account
        response = client.delete(f"/api/accounts/{self.me['id']}")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Try get on all accounts and ensure it really deleted
        response = client.get("/api/accounts/")
        assert response.status_code == 200
        assert len(response.json()) == 0