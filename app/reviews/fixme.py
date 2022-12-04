"""
Test file for accounts route
"""

# Pytest imports
import pytest

# FastAPI imports
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

# SQLAlchemy direct imports
from sqlalchemy.exc import IntegrityError

# Main app import
from ..main import app

# Model imports
from ..accounts.models import AccountCreate
from ..properties.models import PropertyCreate
from .models import ReviewCreate

# Helper function imports from other tests
from ..accounts.test_acccounts import create_account
from ..properties.test_properties import create_property

# Create new client
client: TestClient = TestClient(app)


def create_review(review: ReviewCreate, client_instance: TestClient) -> dict:
    """
    Create a Review object on API, validate, 
    then return the JSON model of it
    """

    # Get review as dictionary and force convert certain types
    review_dict: dict = review.dict()
    review_dict["property_id"] = str(review_dict["property_id"])
    review_dict["poster_id"] = str(review_dict["poster_id"])

    # Send request to create review
    response: Response = client_instance.post(
        f"/api/reviews/", json=review_dict)

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

        # Create accounts for testing
        self.account1 = create_account(
            AccountCreate(
                fname="Maheer",
                lname="Aeron",
                email="maa368@cornell.edu"
            ),
            client_instance=client
        )

        self.account2 = create_account(
            AccountCreate(
                fname="Mayank",
                lname="Rao",
                email="ms3293@cornell.edu"
            ),
            client_instance=client
        )

        self.account3 = create_account(
            AccountCreate(
                fname="Brett",
                lname="Schelsinger",
                email="bgs59@cornell.edu"
            ),
            client_instance=client
        )

        # Create properties for testing
        self.property1 = create_property(
            PropertyCreate(
                owner_id=self.account1['id'],
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

        self.property2 = create_property(
            PropertyCreate(
                owner_id=self.account1['id'],
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

        self.property3 = create_property(
            PropertyCreate(
                owner_id=self.account1['id'],
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

        # Create one review for testing
        self.review1 = create_review(
            ReviewCreate(
                property_id=self.property1["id"],
                poster_id=self.account1["id"],
                rating=5,
                content="I like it!"
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

    def test_get_all_reviews(self):
        
        # Make second review
        review2: dict = create_review(
            ReviewCreate(
                property_id=self.property2["id"],
                poster_id=self.account2["id"],
                rating=2,
                content="I hate it!"
            ),
            client_instance=client
        )

        # Make third review
        review3: dict = create_review(
            ReviewCreate(
                property_id=self.property3["id"],
                poster_id=self.account3["id"],
                rating=3.5,
                content="I'm meh about it"
            ),
            client_instance=client
        )

        # Call get for all reviews
        response = client.get("/api/reviews/")
        assert len(response.json()) == 3

    def test_get_review(self):
        # Call get on review1 and store fetched review
        response = client.get(f"/api/reviews/{self.review1['id']}")
        fetched_review: dict = response.json()

        # Check review properties itself
        assert fetched_review["id"] == self.review1["id"]
        assert fetched_review["property_id"] == self.review1["property_id"]
        assert fetched_review["poster_id"] == self.review1["poster_id"]
        assert fetched_review["rating"] == self.review1["rating"]
        assert fetched_review["content"] == self.review1["content"]
        assert fetched_review["created"] == self.review1["created"]

    ### TEST HTTP POST FUNCTIONS ###

    def test_create_review(self):
        # Setup already creates an account. Just check it
        assert self.review1["property_id"] == self.property1["id"]
        assert self.review1["poster_id"] == self.account1["id"]
        assert self.review1["rating"] == 5
        assert self.review1["content"] == "I like it!"

    def test_create_duplicate_review(self):

        try:

            # Create another review thats duplicate
            create_review(
                ReviewCreate(
                    property_id=self.property1["id"],
                    poster_id=self.account1["id"],
                    rating=5,
                    content="This is my second review"
                ),
                client_instance=client
            )
        except IntegrityError as e:

            # Ensure the error is not null
            assert e is not None

    ### TEST HTTP PATCH FUNCTIONS ###

    def test_update_property(self):

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
