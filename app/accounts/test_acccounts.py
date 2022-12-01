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
from ..accounts.models import AccountCreate

# Create new client
client: TestClient = TestClient(app)

### GLOBAL HELPER FUNCTIONS ###

def create_account(account: AccountCreate, client_instance: TestClient) -> dict:
    """
    Create an Account object on API, validate, 
    then return the JSON model of it
    """

    # Get account as dictionary
    account_dict: dict = account.dict()

    # Send request to create account
    response: Response = client_instance.post("/api/accounts/", json=account_dict)

    # Test and return
    assert response.status_code == 200
    return response.json()


class TestAccounts:

    ### SETUP FUNCTIONS ###

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):

        # Delete everything in database
        response: Response = client.delete("/api/")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Create a new account and save it in the class
        self.account = create_account(
            AccountCreate(
                fname="Maheer", 
                lname="Aeron", 
                email="maa368@cornell.edu"
            ),
            client_instance=client
        )
        
        # Transfer control to a test
        yield

        # Clear everything in database
        response: Response = client.delete("/api/")
        assert response.status_code == 200
        assert response.json() == {"ok": True}


    ### TEST HTTP GET FUNCTIONS ###

    def test_get_all_accounts(self):

        # Make second account
        account2: dict = create_account(
            AccountCreate(
                fname="Mayank", 
                lname="Rao", 
                email="ms3293@cornell.edu"
            ),
            client_instance=client
        )

        # Make third account
        account3: dict = create_account(
            AccountCreate(
                fname="Brett", 
                lname="Schelsinger", 
                email="bgs59@cornell.edu"
            ),
            client_instance=client
        )

        # Now call get on all accounts
        response = client.get("/api/accounts/")

        # Check length of accounts
        accounts: list = response.json()
        assert len(accounts) == 3

    def test_get_account(self):

        # Call get on the stored account in the class
        response = client.get(f"/api/accounts/{self.account['id']}")
        fetched_account: dict = response.json()

        # Check account properties itself
        assert fetched_account["id"] == self.account["id"]
        assert fetched_account["fname"] == self.account["fname"]
        assert fetched_account["lname"] == self.account["lname"]
        assert fetched_account["email"] == self.account["email"]
        assert fetched_account["created"] == self.account["created"]

    ### TEST HTTP POST FUNCTIONS ###

    def test_create_account(self):

        # Setup already creates an account. Just check it
        assert self.account["fname"] == "Maheer"
        assert self.account["lname"] == "Aeron"
        assert self.account["email"] == "maa368@cornell.edu"

    ### TEST HTTP PATCH FUNCTIONS ###

    def test_update_account(self):

        # Try updating account
        response = client.patch(
            f"/api/accounts/{self.account['id']}",
            json={
                "fname": "Mahee",
                "lname": "Aero",
                "email": "maa368@cornell.ed"
            }
        )
        assert response.status_code == 200

        # Now issue a get and test the fields
        response = client.get(f"/api/accounts/{self.account['id']}")
        fetched_account: dict = response.json()

        assert fetched_account["fname"] == "Mahee"
        assert fetched_account["lname"] == "Aero"
        assert fetched_account["email"] == "maa368@cornell.ed"

    ### TEST HTTP DELETE FUNCTIONS ###

    def test_delete_account(self):

        # Delete account
        response = client.delete(f"/api/accounts/{self.account['id']}")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Try get on all accounts and ensure it really deleted
        response = client.get("/api/accounts/")
        assert response.status_code == 200
        assert len(response.json()) == 0