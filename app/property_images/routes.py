"""
Contains route endpoints to access Property Images
"""

# FastAPI imports
from fastapi import APIRouter, Depends, Query, Path, Body, File, UploadFile, HTTPException

# SQLModel imports
from sqlmodel import Session, select

# Azure Blobl imports
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Model imports
from .models import PropertyImage, PropertyImageRead

# Dependency imports
from ..dependencies import get_session, get_blob

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
    blob_service_client: BlobServiceClient = Depends(get_blob),
    property_id: uuid.UUID = Path(),
    upload_file: UploadFile = File(),
):

    # Ensure file is supported type
    if upload_file.content_type not in ("image/png", "image/jpg", "image/jpeg"):
        raise HTTPException(
            status_code=400, detail="Unsupported image file type")

    # Used for finalizing the database entry's "path" field later
    final_path: str = ""

    # Use local, simulated "blob" storage
    if settings.dev_environment == "local":

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

    # Use azure blob storage
    elif settings.dev_environment == "cloud":

        # Create the blob path
        blob_path: str = f"{property_id}/{upload_file.filename}"
        blob_client: BlobClient = blob_service_client.get_blob_client(container="images", blob=blob_path)
        blob_client.upload_blob(upload_file.file)

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
    blob_service_client: BlobServiceClient = Depends(get_blob),
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

    # Delete image in the file system, either local or cloud
    if settings.dev_environment == "local":
        try:
            os.remove(property_image.path)
        except OSError as e:
            raise HTTPException(
                status_code=404, detail=f"Image not found on file system: {e.filename} - {e.strerror}")
    elif settings.dev_environment == "cloud":
        try:
            blob_client: BlobClient = blob_service_client.get_blob_client(container="images", blob=property_image.path)
            blob_client.delete_blob()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"There was an error trying to delete image on cloud {e}")

    # Commit to DBMS
    session.delete(property_image)
    session.commit()

    # Return back an OK response
    return {"ok": True}
