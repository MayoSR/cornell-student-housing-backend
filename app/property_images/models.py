"""
Contains models for Property
"""

# SQL Model imports
from sqlmodel import Field, SQLModel, Relationship

# Standard library imports
import uuid
from datetime import date
from typing import Optional


class PropertyImage(SQLModel, table=True):

    # Table name
    __tablename__ = "property_images"

    # Main Fields
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id")
    path: str = Field(unique=True)
    created: date = Field(default=date.today())

    # Relationships
    property: Optional["Property"] = Relationship()

class PropertyImageRead(SQLModel):
    id: uuid.UUID
    property_id: uuid.UUID
    path: str
    created: date