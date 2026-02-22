import os

from dotenv import load_dotenv

# ===========================
# !!! ATTENTION !!!
# KEEP THIS AT THE TOP TO ENSURE ENVIRONMENT VARIABLES ARE LOADED BEFORE ANY IMPORTS
# ===========================
load_dotenv()

from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.configs import DatabaseConfig
from src.entities import api_router
from src.utils import user_context_dependency


def run_upgrade(connection, alembic_config: Config):
    alembic_config.attributes["connection"] = connection
    command.upgrade(alembic_config, "head")


def ensure_sqlite_directory():
    database_uri = os.getenv("SQLALCHEMY_DATABASE_URI")

    if not database_uri:
        raise ValueError("SQLALCHEMY_DATABASE_URI is not set")

    # Handle only SQLite
    if database_uri.startswith("sqlite"):
        # Remove sqlite driver prefix
        # Example:
        # sqlite+aiosqlite:///database/app_db/app.db
        db_path = database_uri.split("///")[-1]

        # Get directory path
        db_directory = os.path.dirname(db_path)

        if db_directory:
            os.makedirs(db_directory, exist_ok=True)
            print(f"✅ Database directory ensured: {db_directory}")


async def run_migrations():
    ensure_sqlite_directory()
    logger.info("Running migrations if any...")
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option(
        "sqlalchemy.url", os.getenv("SQLALCHEMY_DATABASE_URI")
    )
    async with DatabaseConfig.get_engine().begin() as session:
        await session.run_sync(run_upgrade, alembic_config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting up the application...")
        await run_migrations()
        logger.info("Application started successfully...")
        yield
    except Exception as e:
        logger.exception(e)
        raise
    finally:
        logger.info("Application shutdown complete.")


app = FastAPI(lifespan=lifespan, dependencies=[Depends(user_context_dependency)])


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOW_ORIGINS", "http://localhost, http://127.0.0.1"
        ).split(",")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def check_health():
    return {"response": "Service is healthy!"}


app.include_router(api_router, prefix="/api")
