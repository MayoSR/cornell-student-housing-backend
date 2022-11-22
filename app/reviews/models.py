"""
Contains models for Review
"""

# SQL Model imports
from sqlmodel import Field, SQLModel

# Standard library imports
import uuid
from datetime import date


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id")
    poster_id: uuid.UUID = Field(foreign_key="accounts.id")
    rating: int = Field(default=0)
    content: str = Field(default="")
    created: date = Field(default=date.today())

class ReviewCreate(SQLModel):
    property_id: uuid.UUID
    poster_id: uuid.UUID
    rating: int
    content: str

class ReviewRead(SQLModel):
    id: uuid.UUID
    property_id: uuid.UUID
    poster_id: uuid.UUID
    rating: int
    content: str
    created: date

class ReviewUpdate(SQLModel):
    rating: int | None = None
    content: str | None = None