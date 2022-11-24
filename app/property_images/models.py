"""
Contains models for Property
"""

# SQL Model imports
from sqlmodel import Field, SQLModel, Relationship

# Standard library imports
import uuid
from datetime import date


class PropertyImage(SQLModel, table=True):
    __tablename__ = "property_images"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id")
    path: str = Field(unique=True)
    created: date = Field(default=date.today())

class PropertyImageRead(SQLModel):
    id: uuid.UUID
    property_id: uuid.UUID
    path: str
    created: date