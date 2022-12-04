"""
Contains models for Account
"""

# SQL Model imports
from sqlmodel import Field, SQLModel, Relationship

# Standard library imports
import uuid
from datetime import date


# Other model imports
from ..properties.models import Property


class Account(SQLModel, table=True):

    # Table arguments
    __tablename__ = "accounts"

    # Main fields
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fname: str 
    lname: str
    email: str
    created: date = Field(default=date.today())

class AccountCreate(SQLModel):
    fname: str
    lname: str
    email: str

class AccountRead(SQLModel):
    id: uuid.UUID
    fname: str 
    lname: str
    email: str
    created: date

class AccountUpdate(SQLModel):
    fname: str | None = None
    lname: str | None = None
    email: str | None = None