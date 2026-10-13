
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, engine, check_database_connection
from app import models
from app.routers import categories, products, suppliers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    check_database_connection()

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database connected and tables verified.")
    except SQLAlchemyError as exc:
        logger.error("Database initialization failed: %s", type(exc).__name__)
        raise RuntimeError(
            "Could not initialize the database. Check MySQL permissions."
        ) from None

    yield
    engine.dispose()


app = FastAPI(
    title="Inventory Management API",
    description=(
        "REST API for managing categories, products, and suppliers "
        "using FastAPI, SQLAlchemy ORM, and MySQL."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Inventory Management API is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
def health():
    try:
        check_database_connection()
        return {"status": "healthy", "database": "connected"}
    except RuntimeError:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "unavailable"},
        )


app.include_router(categories.router)
app.include_router(products.router)
app.include_router(suppliers.router)
