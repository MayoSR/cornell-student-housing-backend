from sqlmodel import SQLModel, create_engine
from .config import settings

# Build DB URL from settings
db_url: str = f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_db}"

# Add SSL if necessary
if settings.use_ssl: 
    db_url += "?sslmode=require"

# Print the DB url for logging
print(f"DB has been created: {db_url}")

# Create engine
engine = create_engine(url=db_url)


# Factory function to create DB and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)