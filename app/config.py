"""
Contains settings for API
"""
from fastapi import FastAPI
from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):

    # Define app name
    app_name: str = "Subletters API"

    # Define CORS origins
    backend_cors_origins: list[str]

    # Define postgres host
    postgres_host: str
    postgres_db: str
    postgres_user: str
    postgres_password: str

    # Define Azure Blob settings
    azure_storage_connection_string: str
    azure_storage_container_name: str

    # Specify whether we are on local or cloud development
    dev_environment: str

    class Config:
        env_file = ".env"


# Create new instance of settings class
settings = Settings()
