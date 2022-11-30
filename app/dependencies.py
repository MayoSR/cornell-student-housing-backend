# Database imports
from .database import engine

# SQLModel imports
from sqlmodel import Session

# Settings import
from .config import settings

# Azure Blob imports
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def get_session():
    with Session(engine) as session:
        yield session

def get_blob():
    return BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)