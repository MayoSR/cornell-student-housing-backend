"""
Contains models for Property
"""

# SQL Model imports
from sqlmodel import Field, SQLModel, Relationship

# Standard library imports
import uuid
from datetime import date


class PropertyBase(SQLModel, table=False):
    address: str
    start_date: str
    end_date: str
    monthly_rent: int


class Property(PropertyBase, table=True):
    __tablename__ = "properties"
    id: uuid.UUID = Field(default=uuid.uuid4(), primary_key=True)
    ownerId: uuid.UUID = Field(foreign_key="accounts.id")
    created: date = Field(default=date.today())

class PropertyCreate(PropertyBase):
    """
    """
    ownerId: uuid.UUID

class PropertyRead(PropertyBase):
    id: uuid.UUID
    ownerId: uuid.UUID
    created: date

class PropertyUpdate(SQLModel):
    address: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    monthly_rent: int | None = None
