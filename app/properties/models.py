"""
Contains models for Property
"""

# SQL Model imports
from sqlmodel import Field, SQLModel, Relationship

# Standard library imports
import uuid
from datetime import date
from typing import Optional

# Other model imports
from ..reviews.models import Review
from ..property_images.models import PropertyImage
    
class Property(SQLModel, table=True):

    # Table arguments
    __tablename__ = "properties"

    # Main fields
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="accounts.id")
    name: str
    address: str
    description: str
    start_date: date
    end_date: date
    monthly_rent: int
    num_bedrooms: int
    num_bathrooms: int
    created: date = Field(default=date.today())

    # Relationships
    reviews: list[Review] = Relationship(back_populates="property", sa_relationship_kwargs={"cascade": "delete"})
    images: list[PropertyImage] = Relationship(back_populates="property", sa_relationship_kwargs={"cascade": "delete"})

    account: Optional["Account"] = Relationship()

class PropertyCreate(SQLModel):
    owner_id: uuid.UUID
    name: str
    address: str 
    description: str
    start_date: date
    end_date: date
    monthly_rent: int
    num_bedrooms: int
    num_bathrooms: int
    
class PropertyRead(SQLModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    address: str
    description: str
    start_date: date
    end_date: date
    monthly_rent: int
    num_bedrooms: int
    num_bathrooms: int
    created: date

class PropertyUpdate(SQLModel):
    name: str | None = None
    address: str | None = None
    description: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    monthly_rent: int | None = None
    num_bedrooms: int | None = None
    num_bathrooms: int | None = None