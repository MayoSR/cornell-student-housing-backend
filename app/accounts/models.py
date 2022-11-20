"""
Contains models for Account
"""

# SQL Model imports
from sqlmodel import Field, SQLModel

# Standard library imports
import uuid
from datetime import date
from typing import Optional


class AccountBase(SQLModel, table=False):
    fname: str
    lname: str
    email: str

class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    id: uuid.UUID = Field(default=uuid.uuid4(), primary_key=True)
    fname: str 
    lname: str
    email: str
    created: date = Field(default=date.today())

class AccountCreate(AccountBase):
    pass

class AccountRead(AccountBase):
    id: uuid.UUID
    created: date

class AccountUpdate(SQLModel):
    fname: str | None = None
    lname: str | None = None
    email: str | None = None