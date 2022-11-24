"""
    TODO:
        - Modernize config.py
        - Create models.py for accounts
        - Create schemas.py for accounts
        - Create crud.py for accounts, but may need to play with DB
        - Create v1.py for accounts, but may need to play with DB
"""

# Core imports
from fastapi import FastAPI

# Starlette imports
from starlette.responses import RedirectResponse

# Middleware imports
from fastapi.middleware.cors import CORSMiddleware

# Settings imports
from .core.config import settings

# Database imports
from .database import create_db_and_tables

# Routers
from .home.routes import router as home_router
from .accounts.routes import router as accounts_router
from .properties.routes import router as property_router
from .property_images.routes import router as property_image_router
from .reviews.routes import router as review_router


def get_application():
    _app = FastAPI(title=settings.app_name)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin)
                       for origin in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize database?
    create_db_and_tables()

    # Adding routers
    _app.include_router(home_router, prefix="/api", tags=["home"])
    _app.include_router(accounts_router, prefix="/api", tags=["accounts"])
    _app.include_router(property_router, prefix="/api", tags=["properties"])
    _app.include_router(property_image_router, prefix="/api", tags=["property_images"])
    _app.include_router(review_router, prefix="/api", tags=["reviews"])

    # Force redirect of the "/" route to "/api"

    @_app.get("/")
    def redirect_home():
        return RedirectResponse(url="/api")

    return _app


app = get_application()
