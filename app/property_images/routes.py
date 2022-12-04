"""
Contains routes to access Property Images
"""

# FastAPI imports
from fastapi import APIRouter, Depends, Query, Path, Body, File, UploadFile, HTTPException

# SQLModel imports
from sqlmodel import Session, select

# Azure Blob imports
from azure.storage.blob import ContainerClient

# Model imports
from .models import PropertyImage, PropertyImageRead

# Dependency imports
from ..dependencies import get_session, get_container_client

# Settings import
from ..config import settings

# Standard library imports
import uuid
import os


# Initializing router
router = APIRouter(prefix="/properties")


### HTTP GET FUNCTIONS ###

@router.get("/{property_id}/images", response_model=list[PropertyImageRead])
def get_all_property_images(
    *,
    session: Session = Depends(get_session),
    property_id: uuid.UUID = Path(),
    offset: int = Query(default=0),
    limit: int = Query(default=100, lte=100),
):
    """
    Get all the images for a particular property
    """

    # Get property images with filter on property_id
    property_images = session.exec(select(PropertyImage)
                                   .where(PropertyImage.property_id == property_id)
                                   .offset(offset)
                                   .limit(limit))\
        .all()

    # Return list of property images
    return property_images

### HTTP POST FUNCTIONS ###


@router.post("/{property_id}/images", response_model=PropertyImageRead)
def create_property_image(
    *,
    session: Session = Depends(get_session),
    container_client: ContainerClient = Depends(get_container_client),
    property_id: uuid.UUID = Path(),
    upload_file: UploadFile = File(),
):

    # Ensure file is supported type
    if upload_file.content_type not in ("image/png", "image/jpg", "image/jpeg"):
        raise HTTPException(
            status_code=400, detail="Unsupported image file type")

    # Used for finalizing the database entry's "path" field later
    final_path: str = ""

    # Use settings to track if we upload to azure blob or local
    if not settings.use_azure_blob:

        # If "/blob" doesn't have a subfolder for the property id, make it
        subfolder: str = f"blob/{property_id}"
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)

        # Now create the path and save the image
        path: str = f"{subfolder}/{upload_file.filename}"
        with open(path, "wb+") as file_obj:
            file_obj.write(upload_file.file.read())

        # Set the final path
        final_path = os.path.abspath(path)

    else:

        # Create the blob path
        blob_path: str = f"{property_id}/{upload_file.filename}"
        container_client.upload_blob(name=blob_path, data=upload_file.file)

        # Set the final path
        final_path = blob_path

    
    # Now create the database entry 
    db_property_image = PropertyImage(property_id=property_id, path=final_path)

    # Commit to DBMS
    session.add(db_property_image)
    session.commit()
    session.refresh(db_property_image)

    # Return back property image
    return db_property_image

### HTTP DELETE FUNCTIONS ###

@router.delete("/{property_id}/images/{property_image_id}")
def delete_property_image(
    *,
    session: Session = Depends(get_session),
    container_client: ContainerClient = Depends(get_container_client),
    property_id: uuid.UUID = Path(),
    property_image_id: uuid.UUID = Path()
):

    # Get property image and check if it exists
    property_image = session.get(PropertyImage, property_image_id)
    if not property_image:
        raise HTTPException(status_code=404, detail="Property image not found")

    # Ensure property image is part of property id
    if property_image.property_id != property_id:
        raise HTTPException(status_code=400, detail="Specified property ID does not have this image")

    # Use settings to track if we delete on azure blob or local
    if not settings.use_azure_blob:
        try:
            os.remove(property_image.path)
        except OSError as e:
            raise HTTPException(
                status_code=404, detail=f"Image not found on file system: {e.filename} - {e.strerror}")
    else:
        try:
            container_client.delete_blob(blob=property_image.path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"There was an error trying to delete image on cloud {e}")

    # Commit to DBMS
    session.delete(property_image)
    session.commit()

    # Return back an OK response
    return {"ok": True}
