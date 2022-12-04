"""
Contains routes to access Reviews
"""

# SQL Model imports
from sqlmodel import Field, SQLModel, Relationship, UniqueConstraint

# Standard library imports
import uuid
from datetime import date
from typing import Optional


class Review(SQLModel, table=True):

    # Table arguments
    __tablename__ = "reviews"

    # Main Fields
    property_id: uuid.UUID = Field(foreign_key="properties.id", primary_key=True)
    poster_id: uuid.UUID = Field(foreign_key="accounts.id", primary_key=True)
    rating: int = Field(default=0)
    content: str = Field(default="")
    created: date = Field(default=date.today())

class ReviewCreate(SQLModel):
    poster_id: uuid.UUID
    rating: int
    content: str

class ReviewRead(SQLModel):
    property_id: uuid.UUID
    poster_id: uuid.UUID
    rating: int
    content: str
    created: date

class ReviewUpdate(SQLModel):
    rating: int | None = None
    content: str | None = None