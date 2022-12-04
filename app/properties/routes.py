"""
Contains routes to access Properties
"""

# FastAPI imports
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException

# SQLModel imports
from sqlmodel import Session, select

# Azure Blob imports
from azure.storage.blob import ContainerClient

# Model imports
from .models import Property, PropertyCreate, PropertyRead, PropertyUpdate
from ..property_images.models import PropertyImage

# Dependency imports
from ..dependencies import get_session, get_container_client

# Settings import
from ..config import settings

# Standard library imports
import uuid
import os
import shutil


# Initializing router
router = APIRouter(prefix="/properties")


### HTTP GET FUNCTIONS ###

@router.get("/", response_model=list[PropertyRead])
def get_all_properties(
    *,
    owner_id: uuid.UUID | None = Query(default=None),
    session: Session = Depends(get_session),
    offset: int = Query(default=0),
    limit: int = Query(default=100, lte=100),
):
    # Get properties with filter on owner_id
    properties = session.exec(select(Property)
                              .where((Property.owner_id == owner_id) if owner_id else (Property is not None))
                              .offset(offset)
                              .limit(limit))\
        .all()

    # Return list of properties
    return properties


@router.get("/{property_id}", response_model=PropertyRead)
def get_property_by_id(
    *,
    session: Session = Depends(get_session),
    property_id: uuid.UUID = Path()
):
    # Get property and check if it exists
    property = session.get(Property, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    # Return back property
    return property


### HTTP POST FUNCTIONS ###

@router.post("/", response_model=PropertyRead)
def create_property(
    *,
    session: Session = Depends(get_session),
    property: PropertyCreate = Body()
):

    # Create property by using from_orm function
    db_property = Property.from_orm(property)

    # Commit to DBMS
    session.add(db_property)
    session.commit()
    session.refresh(db_property)

    # Return back property
    return db_property


### HTTP PATCH FUNCTIONS ###

@router.patch("/{property_id}", response_model=PropertyRead)
def update_property(
    *,
    session: Session = Depends(get_session),
    property_id: uuid.UUID = Path(),
    property: PropertyUpdate = Body()
):

    # Check if propery exists
    db_property = session.get(Property, property_id)
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")

    # Update property data
    property_data = property.dict(exclude_unset=True)
    for key, value in property_data.items():
        setattr(db_property, key, value)

    # Commit to DBMS
    session.add(db_property)
    session.commit()
    session.refresh(db_property)

    # Return back property
    return db_property


### HTTP DELETE FUNCTIONS ###

@router.delete("/{property_id}")
def delete_property(
    *,
    session: Session = Depends(get_session),
    property_id: uuid.UUID = Path(),
    container_client: ContainerClient = Depends(get_container_client),
):

    # Get property and check if it exists
    property = session.get(Property, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    # Commit to DBMS
    session.delete(property)
    session.commit()

    # Now try to delete property images associated with this
    if not settings.use_azure_blob:
        try:
            path = f"blob/{property_id}"
            if os.path.exists(path):
                shutil.rmtree(path)
        except OSError as e:
            raise HTTPException(
                status_code=404, detail=f"There were images for property id: {property_id} but there was an error deleting existing images")
    else:
        blobs =  [blob.name for blob in container_client.list_blobs(name_starts_with=f"{property_id}")]
        blobs.sort(reverse=True, key=len)
        if len(blobs) > 0:
            for blob in blobs:
                container_client.delete_blob(blob)

    # Return back an OK response
    return {"ok": True}