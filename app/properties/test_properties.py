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


class TestProperties:

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

        # Create a new global property and save it
        response = client.post(
            "/api/properties/",
            json={
                "owner_id": f"{self.me['id']}",
                "address": "715 E State St.",
                "start_date": "2022-11-29",
                "end_date": "2023-11-29",
                "monthly_rent": 2100,
                "num_bedrooms": 1,
                "num_bathrooms": 1
            }
        )
        assert response.status_code == 200
        self.property = response.json()

        # Transfer control to a test
        yield

        # Clear everything in database
        response: Response = client.delete("/api/")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

    ### TEST HTTP GET FUNCTIONS ###

    def test_get_all_properties(self):
        
        # Make second property
        response: Response = client.post(
            "/api/properties/",
            json={
                "owner_id": f"{self.me['id']}",
                "address": "123 Place",
                "start_date": "2022-12-29",
                "end_date": "2023-12-29",
                "monthly_rent": 500,
                "num_bedrooms": 1,
                "num_bathrooms": 2
            }
        )
        assert response.status_code == 200

        # Make third property
        response: Response = client.post(
            "/api/properties/",
            json={
                "owner_id": f"{self.me['id']}",
                "address": "567 Street",
                "start_date": "2022-10-29",
                "end_date": "2023-10-29",
                "monthly_rent": 1000,
                "num_bedrooms": 3,
                "num_bathrooms": 3
            }
        )
        assert response.status_code == 200

        # Call get for all properties
        response = client.get("/api/properties/")
        assert len(response.json()) == 3

    def test_get_property(self):

        # Call get on me and store the fetched acc
        response = client.get(f"/api/properties/{self.property['id']}")
        fetched_property: dict = response.json()

        # Check account properties itself
        assert fetched_property["id"] == self.property["id"]
        assert fetched_property["owner_id"] == self.me["id"]
        assert fetched_property["address"] == self.property["address"]
        assert fetched_property["start_date"] == self.property["start_date"]
        assert fetched_property["end_date"] == self.property["end_date"]
        assert fetched_property["monthly_rent"] == self.property["monthly_rent"]
        assert fetched_property["num_bedrooms"] == self.property["num_bedrooms"]
        assert fetched_property["num_bathrooms"] == self.property["num_bathrooms"]
        assert fetched_property["created"] == self.property["created"]

    ### TEST HTTP POST FUNCTIONS ###

    def test_create_property(self):
        """
        Tests for creating an account
        """

        # Setup already creates an account. Just check it
        assert self.property["owner_id"] == self.me["id"]
        assert self.property["address"] == "715 E State St."
        assert self.property["start_date"] == "2022-11-29"
        assert self.property["end_date"] == "2023-11-29"
        assert self.property["monthly_rent"] == 2100
        assert self.property["num_bedrooms"] == 1
        assert self.property["num_bathrooms"] == 1

    ### TEST HTTP PATCH FUNCTIONS ###

    def test_update_property(self):
        pass

        # Try updating property
        response = client.patch(
            f"/api/properties/{self.property['id']}",
            json={
                "address": "715 St",
                "monthly_rent": 1000
            }
        )
        assert response.status_code == 200

        # Now issue a get and test the fields
        response = client.get(f"/api/properties/{self.property['id']}")
        fetched_property: dict = response.json()

        assert fetched_property["address"] == "715 St"
        assert fetched_property["monthly_rent"] == 1000

    ### TEST HTTP DELETE FUNCTIONS ###

    def test_delete_property(self):

        # Delete property
        response = client.delete(f"/api/properties/{self.property['id']}")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Try get on all properties and ensure it really deleted
        response = client.get("/api/properties/")
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_delete_property_via_account(self):

        # Delete account which cascades to property
        response = client.delete(f"/api/accounts/{self.me['id']}")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Try get on all properties and ensure it really deleted
        response = client.get("/api/properties/")
        assert response.status_code == 200
        assert len(response.json()) == 0