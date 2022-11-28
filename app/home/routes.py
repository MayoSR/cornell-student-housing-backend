# FastAPI imports
from fastapi import APIRouter, Depends

# SQLModel imports
from sqlmodel import Session, select

# Model imports
from ..accounts.models import Account
from ..properties.models import Property
from ..property_images.models import PropertyImage
from ..reviews.models import Review

# Dependency imports
from ..dependencies import get_session

# Settings import
from ..core.config import settings

# Standard library imports
import os

# Initializing router
router = APIRouter()

@router.get("/")
def get_home():
    return "Welcome to the Subeletters-API home!"

@router.delete("/")
def delete_all(session: Session = Depends(get_session)):
    """
    THIS IS DANGEROUS! Should only be used for testing
    """

    # Delete all models
    session.delete(Review)
    session.delete(PropertyImage)
    session.delete(Property)
    session.delete(Account)

    # If local, delete blob folder
    if settings.dev_environment == "local":
        os.rmdir("/blob")

    # Return ok status
    return {"ok": True}