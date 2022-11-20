from sqlmodel import SQLModel, create_engine
from .core.config import settings
db_url: str = f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_db}"
engine = create_engine(url=db_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)