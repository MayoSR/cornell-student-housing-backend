"""
Contains models for Property
"""

# SQL Model imports
from sqlmodel import Field, SQLModel, Relationship

# Standard library imports
import uuid
from datetime import date


class Property(SQLModel, table=True):
    __tablename__ = "properties"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ownerId: uuid.UUID = Field(foreign_key="accounts.id")
    address: str
    start_date: date
    end_date: date
    monthly_rent: int
    num_bedrooms: int
    num_bathrooms: int
    created: date = Field(default=date.today())

class PropertyCreate(SQLModel):
    ownerId: uuid.UUID
    address: str 
    start_date: date
    end_date: date
    monthly_rent: int
    num_bedrooms: int
    num_bathrooms: int
    
class PropertyRead(SQLModel):
    id: uuid.UUID
    ownerId: uuid.UUID
    address: str
    start_date: date
    end_date: date
    monthly_rent: int
    num_bedrooms: int
    num_bathrooms: int
    created: date

class PropertyUpdate(SQLModel):
    address: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    monthly_rent: int | None = None
    num_bedrooms: int | None = None
    num_bathrooms: int | None = None