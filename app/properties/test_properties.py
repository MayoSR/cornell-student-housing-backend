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
from ..properties.models import PropertyCreate

# Helper function imports from other tests
from ..accounts.test_acccounts import create_account



# Create new client
client: TestClient = TestClient(app)


### GLOBAL HELPER FUNCTIONS ###

def create_property(property: PropertyCreate, client_instance: TestClient) -> dict:
    """
    Create an Property object on API, validate, 
    then return the JSON model of it
    """

    # Get property as dictionary and force convert certain types
    property_dict: dict = property.dict()        
    property_dict["owner_id"] = str(property_dict["owner_id"])
    property_dict["start_date"] = str(property_dict["start_date"])
    property_dict["end_date"] = str(property_dict["end_date"])

    # Send request to create property
    response: Response = client_instance.post("/api/properties/", json=property_dict)

    # Test and return
    assert response.status_code == 200
    return response.json()

class TestProperties:
    
    ### SETUP FUNCTIONS ###

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):

        # Delete everything in database
        response: Response = client.delete("/api/")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Create a new global account and save it
        self.account = create_account(
            AccountCreate(
                fname="Maheer", 
                lname="Aeron", 
                email="maa368@cornell.edu"
            ),
            client_instance=client
        )


        # Create a new global property and save it
        self.property = create_property(
            PropertyCreate(
                owner_id=self.account['id'],
                name="College Town Terrace",
                address="715 E State St.",
                description="This is a big apartment in Ithaca",
                start_date="2022-11-30",
                end_date="2023-11-30",
                monthly_rent=2100,
                num_bedrooms=1,
                num_bathrooms=1
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

    def test_get_all_properties(self):

        # Make second property
        property2: dict = create_property(
            PropertyCreate(
                owner_id=self.account['id'],
                name="Lux Apartments",
                address="123 place",
                description="This is some complex in college town",
                start_date="2022-11-30",
                end_date="2023-11-30",
                monthly_rent=1500,
                num_bedrooms=2,
                num_bathrooms=2
            ),
            client_instance=client
        )

        # Make third property
        property3: dict = create_property(
            PropertyCreate(
                owner_id=self.account['id'],
                name="Cornell Dorms",
                address="Hoy Road",
                description="This is a dorm in Cornell",
                start_date="2022-11-30",
                end_date="2023-11-30",
                monthly_rent=1000,
                num_bedrooms=3,
                num_bathrooms=2
            ),
            client_instance=client
        )

        # Call get for all properties
        response = client.get("/api/properties/")
        assert len(response.json()) == 3

    def test_get_property(self):
        # Call get property stored in the class and store it
        response = client.get(f"/api/properties/{self.property['id']}")
        fetched_property: dict = response.json()

        # Check account properties itself
        assert fetched_property["id"] == self.property["id"]
        assert fetched_property["name"] == self.property["name"]
        assert fetched_property["owner_id"] == self.account["id"]
        assert fetched_property["address"] == self.property["address"]
        assert fetched_property["description"] == self.property["description"]
        assert fetched_property["start_date"] == self.property["start_date"]
        assert fetched_property["end_date"] == self.property["end_date"]
        assert fetched_property["monthly_rent"] == self.property["monthly_rent"]
        assert fetched_property["num_bedrooms"] == self.property["num_bedrooms"]
        assert fetched_property["num_bathrooms"] == self.property["num_bathrooms"]
        assert fetched_property["created"] == self.property["created"]

    ### TEST HTTP POST FUNCTIONS ###

    def test_create_property(self):
        # Setup already creates an property. Just check it
        assert self.property["owner_id"] == self.account["id"]
        assert self.property["name"] == "College Town Terrace"
        assert self.property["address"] == "715 E State St."
        assert self.property["description"] == "This is a big apartment in Ithaca"
        assert self.property["start_date"] == "2022-11-30"
        assert self.property["end_date"] == "2023-11-30"
        assert self.property["monthly_rent"] == 2100
        assert self.property["num_bedrooms"] == 1
        assert self.property["num_bathrooms"] == 1

    ### TEST HTTP PATCH FUNCTIONS ###

    def test_update_property(self):

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
        response = client.delete(f"/api/accounts/{self.account['id']}")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Try get on all properties and ensure it really deleted
        response = client.get("/api/properties/")
        assert response.status_code == 200
        assert len(response.json()) == 0