"""
Contains route endpoints to access Property Images
"""

# FastAPI imports
from fastapi import APIRouter, Depends, Query, Path, Body, File, UploadFile, HTTPException

# SQLModel imports
from sqlmodel import Session, select

# Model imports
from .models import PropertyImage, PropertyImageRead

# Dependency imports
from ..dependencies import get_session

# Settings import
from ..core.config import settings

# Standard library imports
import uuid
import os


# Initializing router
router = APIRouter(prefix="/properties/images")


### HTTP GET FUNCTIONS ###

@router.get("/", response_model=list[PropertyImage])
def get_all_property_images(
    *,
    property_id: uuid.UUID | None = Query(default=None),
    session: Session = Depends(get_session),
    offset: int = Query(default=0),
    limit: int = Query(default=100, lte=100),
):
    """
    This will not return the database entries.
    Instead, it will give the actual images
    """

    # Get property images with filter on property_id
    property_images = session.exec(select(PropertyImage)
                                   .where((PropertyImage.property_id == property_id) if property_id else (PropertyImage is not None))
                                   .offset(offset)
                                   .limit(limit))\
        .all()

    # Return list of property images
    return property_images


@router.get("/{property_image_id}", response_model=PropertyImageRead)
def get_property_image_by_id(
    *,
    session: Session = Depends(get_session),
    property_image_id: uuid.UUID = Path()
):
    # Get property_image and check if it exists
    property_image = session.get(PropertyImage, property_image_id)
    if not property_image:
        raise HTTPException(status_code=404, detail="Property Image not found")

    # Return back property image
    return property_image


### HTTP POST FUNCTIONS ###

@router.post("/{property_id}")
def create_property_image(
    *,
    session: Session = Depends(get_session),
    property_id: uuid.UUID = Path(),
    property_image_upload_file: UploadFile = File(),
):
    """
    TODO:
        - Is there a smarter way to specify property id and the image?
        - Should these be separate post requests?
    """

    # Check environment
    if settings.dev_environment == "local":

        # Ensure file is supported type
        if property_image_upload_file.content_type not in ("image/png", "image/jpg", "image/jpeg"):
            raise HTTPException(
                status_code=400, detail="Unsupported image file type")

        # Create subfolder in "/blob" for property id if not found
        # Then save the file
        base_path: str = f"blob/{property_id}"
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        # Now create the path and save the image
        path: str = f"{base_path}/{property_image_upload_file.filename}"
        with open(path, "wb+") as file_obj:
            file_obj.write(property_image_upload_file.file.read())

        # Now create a DB entry for the image
        abs_path = os.path.abspath(path)
        db_property_image = PropertyImage(
            property_id=property_id, path=abs_path)

        # Commit to DBMS
        session.add(db_property_image)
        session.commit()
        session.refresh(db_property_image)

        # Return back property image
        return db_property_image

    # Currently, cloud is not supported
    else:
        raise HTTPException(
            status_code=501, detail="Image uploading to cloud not yet supported")


### HTTP DELETE FUNCTIONS ###

@router.delete("/{property_image_id}")
def delete_property_image(
    *,
    session: Session = Depends(get_session),
    property_image_id: uuid.UUID = Path()
):

    # Get property image and check if it exists
    property_image = session.get(PropertyImage, property_image_id)
    if not property_image:
        raise HTTPException(status_code=404, detail="Property image not found")

    # Delete image in file system
    if settings.dev_environment == "local":
        try:
            os.remove(property_image.path)
        except OSError as e:
            raise HTTPException(
                status_code=404, detail=f"Image not found on file system: {e.filename} - {e.strerror}")
    else:
        raise HTTPException(
            status_code=501, detail="Image deleting on cloud not yet supported")

    # Commit to DBMS
    session.delete(property_image)
    session.commit()

    # Return back an OK response
    return {"ok": True}
