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


def get_container_client() -> ContainerClient | None:
    if settings.use_azure_blob:
        return ContainerClient.from_connection_string(
            conn_str=settings.azure_storage_connection_string,
            container_name=settings.azure_storage_container_name,
        )
    else:
        return None