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

    # Specify whether we are on local development
    # or cloud development
    dev_environment = "local"

    class Config:
        env_file = ".env"


# Create new instance of settings class
settings = Settings()