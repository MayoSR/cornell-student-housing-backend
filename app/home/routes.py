# FastAPI imports
from fastapi import APIRouter, Depends

# SQLModel imports
from sqlmodel import Session, select, delete

# Model imports
from ..accounts.models import Account
from ..properties.models import Property
from ..property_images.models import PropertyImage
from ..reviews.models import Review

# Dependency imports
from ..dependencies import get_session

# Settings import
from ..config import settings

# Standard library imports
import os
import shutil

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
    
    # Delete everything
    session.exec(delete(Review))
    session.exec(delete(PropertyImage))
    session.exec(delete(Property))
    session.exec(delete(Account))

    # Commit the delete
    session.commit()

    # If local, delete blob folder
    if not settings.use_azure_blob:
        if os.path.exists("blob/"):
            shutil.rmtree("blob/")

    # Return ok status
    return {"ok": True}