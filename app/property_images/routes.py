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

# Standard library imports
import uuid

# Setting import
from ..core.config import settings


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

    # First, check if we are on local development or cloud
    if settings.dev_environment == "local":

        # Must ensure that file type is supported
        if property_image_upload_file.content_type not in ("image/png", "image/jpg", "image/jpeg"):
            print(property_image_upload_file.content_type)
            raise HTTPException(
                status_code=400, detail="Unsupported image file type")

        # Otherwise, save this file locally
        path = f"blob/{property_id}/{property_image_upload_file.filename}"
        with open(path, "wb+") as file_obj:
            file_obj.write(property_image_upload_file.file.read())

        # Now, create a DB entry for it
        db_property_image = PropertyImage(property_id=property_id, path=path)

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

    # Commit to DBMS
    session.delete(property_image)
    session.commit()

    # Return back an OK response
    return {"ok": True}
