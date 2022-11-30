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

    ### HELPER FUNCTIONS ###

    def __create_account(self, fname, lname, email) -> dict:
        """
        Creates an account on the API and returns the json of it
        """
        response: Response = client.post(
            "/api/accounts/",
            json={
                "fname": fname,
                "lname": lname,
                "email": email
            }
        )
        assert response.status_code == 200
        return response.json()

    def __create_property(self, owner_id, address, start_date, end_date, monthly_rent, num_bedrooms, num_bathrooms) -> dict:
        """
        Creates a property on the API and returns the json of it
        """
        response: Response = client.post(
            "/api/properties/",
            json={
                "owner_id": owner_id,
                "address": address,
                "start_date": start_date,
                "end_date": end_date,
                "monthly_rent": monthly_rent,
                "num_bedrooms": num_bedrooms,
                "num_bathrooms": num_bathrooms
            }
        )
        assert response.status_code == 200
        return response.json()

    def __create_review(self, property_id, poster_id, rating, content) -> dict:
        """
        Creates a review on the API and returns the json of it
        """
        response: Response = client.post(
            "/api/reviews/",
            json={
                "property_id": property_id,
                "poster_id": poster_id,
                "rating": rating,
                "content": content
            }
        )
        assert response.status_code == 200
        return response.json()

    ### SETUP FUNCTIONS ###

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):

        # Delete everything in database
        response: Response = client.delete("/api/")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Create accounts for testing
        self.acc1 = self.__create_account(
            fname="Maheer", 
            lname="Aeron", 
            email="maa368@cornell.edu"
        )

        self.acc2 = self.__create_account(
            fname="Mayank", 
            lname="Rao", 
            email="ms3293@cornell.edu"
        )

        self.acc3 = self.__create_account(
            fname="Brett", 
            lname="Schelsinger", 
            email="bgs59@cornell.edu"
        )

        # Create properties for testing
        self.prop1 = self.__create_property(
            owner_id=self.acc1["id"],
            address="715 E State St.",
            start_date="2022-11-29",
            end_date="2023-11-29",
            monthly_rent=2100,
            num_bedrooms=1,
            num_bathrooms=1
        )

        self.prop2 = self.__create_property(
            owner_id=self.acc2["id"],
            address="123 Street",
            start_date="2022-11-29",
            end_date="2023-11-29",
            monthly_rent=500,
            num_bedrooms=2,
            num_bathrooms=2
        )

        self.prop3 = self.__create_property(
            owner_id=self.acc3["id"],
            address="425 Avenue",
            start_date="2022-11-29",
            end_date="2023-11-29",
            monthly_rent=1500,
            num_bedrooms=2,
            num_bathrooms=2
        )

        # Create one review for testing
        self.review1 = self.__create_review(
            property_id=self.prop1["id"],
            poster_id=self.acc1["id"],
            rating=5,
            content="I like it"
        )

        # Transfer control to a test
        yield

        # Clear everything in database
        response: Response = client.delete("/api/")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

    ### TEST HTTP GET FUNCTIONS ###

    def test_get_all_reviews(self):

        # Make second review
        review2: dict = self.__create_review(
            property_id=self.prop2["id"],
            poster_id=self.acc2["id"],
            rating=5,
            content="I hate it"
        )

        review3: dict = self.__create_review(
            property_id=self.prop3["id"],
            poster_id=self.acc3["id"],
            rating=5,
            content="I'm meh about it"
        )

        # Call get for all reviews
        response = client.get("/api/reviews/")
        assert len(response.json()) == 3

    def test_get_review(self):

        # Call get on acc1 and store fetched review
        response = client.get(f"/api/reviews/{self.review1['id']}")
        fetched_review: dict = response.json()

        # Check account properties itself
        assert fetched_review["id"] == self.review1["id"]
        assert fetched_review["property_id"] == self.review1["property_id"]
        assert fetched_review["poster_id"] == self.review1["poster_id"]
        assert fetched_review["rating"] == self.review1["rating"]
        assert fetched_review["content"] == self.review1["content"]
        assert fetched_review["created"] == self.review1["created"]

    ### TEST HTTP POST FUNCTIONS ###

    def test_create_review(self):
        """
        Tests for creating an account
        """

        # Setup already creates an account. Just check it
        assert self.review1["property_id"] == self.prop1["id"]
        assert self.review1["poster_id"] == self.acc1["id"]
        assert self.review1["rating"] == 5
        assert self.review1["content"] == "I like it"

    ### TEST HTTP PATCH FUNCTIONS ###

    def test_update_property(self):
        pass

        # Try updating review
        response = client.patch(
            f"/api/reviews/{self.review1['id']}",
            json={
                "rating": 3,
                "content": "I don't like it anymore"
            }
        )
        assert response.status_code == 200

        # Now issue a get and test the fields
        response = client.get(f"/api/reviews/{self.review1['id']}")
        fetched_review: dict = response.json()

        assert fetched_review["rating"] == 3
        assert fetched_review["content"] == "I don't like it anymore"

    ### TEST HTTP DELETE FUNCTIONS ###

    def test_delete_review(self):
        # Delete review
        response = client.delete(f"/api/reviews/{self.review1['id']}")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Try get on all properties and ensure it really deleted
        response = client.get("/api/reviews/")
        assert response.status_code == 200
        assert len(response.json()) == 0
