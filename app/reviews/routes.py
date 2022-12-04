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
router = APIRouter(prefix="/properties")


### HTTP GET FUNCTIONS ###

@router.get("/{property_id}/reviews", response_model=list[Review])
def get_all_reviews(
    *,
    session: Session = Depends(get_session),
    property_id: uuid.UUID = Path(),
    offset: int = Query(default=0),
    limit: int = Query(default=100, lte=100),
):

    # Get property images with filter on property_id
    reviews = session.exec(select(Review)
                           .where(Review.property_id == property_id)
                           .offset(offset)
                           .limit(limit))\
        .all()

    # Return list of reviews
    return reviews

### HTTP POST FUNCTIONS ###


@router.post("/{property_id}/reviews", response_model=ReviewRead)
def create_review(
    *,
    session: Session = Depends(get_session),
    property_id: uuid.UUID = Path(),
    review: ReviewCreate = Body()
):

    # Create review
    db_review = Review(
        property_id=property_id,
        poster_id=review.poster_id,
        rating=review.rating,
        content=review.content
    )

    # Commit to DBMS
    session.add(db_review)
    session.commit()
    session.refresh(db_review)

    # Return back review
    return db_review


### HTTP PATCH FUNCTIONS ###

@router.patch("/{property_id}/reviews/{account_id}", response_model=ReviewRead)
def update_review(
    *,
    session: Session = Depends(get_session),
    property_id: uuid.UUID = Path(),
    account_id: uuid.UUID = Path(),
    review: ReviewUpdate = Body()
):

    # Check if review exists
    db_review = session.get(Review, (property_id, account_id))
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

@router.delete("/{property_id}/reviews/{account_id}")
def delete_review(
    *,
    session: Session = Depends(get_session),
    property_id: uuid.UUID = Path(),
    account_id: uuid.UUID = Path(),
):

    # Get review and check if it exists
    review = session.get(Review, (property_id, account_id))
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Commit to DBMS
    session.delete(review)
    session.commit()

    # Return back an OK response
    return {"ok": True}
