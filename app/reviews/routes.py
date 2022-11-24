"""
Contains route endpoints to access Reviews

TODO:
 - Get all reviews by property
 - Test update and delete 
"""

# FastAPI imports
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException

# SQLModel imports
from sqlmodel import Session, select

# Model imports
from .models import Review, ReviewCreate, ReviewRead, ReviewUpdate

# Dependency imports
from ..dependencies import get_session

# Standard library imports
import uuid


# Initializing router
router = APIRouter(prefix="/reviews")


### HTTP GET FUNCTIONS ###

@router.get("/", response_model=list[Review])
def get_all_reviews(
    *,
    property_id: uuid.UUID | None = Query(default=None),
    session: Session = Depends(get_session),
    offset: int = Query(default=0),
    limit: int = Query(default=100, lte=100),
):
    # Get reviews with filter on property id
    reviews = session.exec(select(Review)
                           .where((Review.property_id == property_id) if property_id else (Review is not None))
                           .offset(offset)
                           .limit(limit))\
        .all()

    # Return list of reviews
    return reviews


@router.get("/{review_id}", response_model=Review)
def get_review_by_id(
    *,
    session: Session = Depends(get_session),
    review_id: uuid.UUID = Path()
):
    # Get review and check if it exists
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Return back review
    return review


### HTTP POST FUNCTIONS ###

@router.post("/", response_model=ReviewRead)
def create_review(
    *,
    session: Session = Depends(get_session),
    review: ReviewCreate = Body()
):
    """
    TODO: Need to catch when property and poster id is invalid
    """

    # Create review by using from_orm function
    db_review = Review.from_orm(review)

    # Commit to DBMS
    session.add(db_review)
    session.commit()
    session.refresh(db_review)

    # Return back review
    return db_review


### HTTP PATCH FUNCTIONS ###

@router.patch("/{review_id}", response_model=ReviewRead)
def update_review(
    *,
    session: Session = Depends(get_session),
    review_id: uuid.UUID = Path(),
    review: ReviewUpdate = Body()
):

    # Check if review exists
    db_review = session.get(Review, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Update review data
    review_data = review.dict(exclude_unset=True)
    for key, value in review_data.items():
        setattr(db_review, key, value)

    # Commit to DBMS
    session.add(db_review)
    session.commit()
    session.refresh(db_review)

    # Return back review
    return db_review


### HTTP DELETE FUNCTIONS ###

@router.delete("/{review_id}")
def delete_review(
    *,
    session: Session = Depends(get_session),
    review_id: uuid.UUID = Path()
):

    # Get review and check if it exists
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Commit to DBMS
    session.delete(review)
    session.commit()

    # Return back an OK response
    return {"ok": True}
