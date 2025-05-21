import asyncio
import os
from contextlib import asynccontextmanager
from threading import Thread

from alembic import command
from alembic.config import Config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.config import DatabaseConfig
from src.controllers import api_router
from src.tasks import FileQueueProcessor

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("interval", seconds=int(os.getenv("SCHEDULER_INTERVAL")))
async def scheduled_job():
    try:
        async with FileQueueProcessor() as processor:
            await processor.process()
    except Exception as e:
        logger.exception(e)


def run_upgrade(connection, alembic_config: Config):
    alembic_config.attributes["connection"] = connection
    command.upgrade(alembic_config, "head")


async def run_migrations():
    logger.info("Running migrations if any...")
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option(
        "sqlalchemy.url", os.getenv("SQLALCHEMY_DATABASE_URI")
    )
    async with DatabaseConfig.get_engine().begin() as session:
        await session.run_sync(run_upgrade, alembic_config)


def run_scheduler():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    scheduler.start()
    loop.run_forever()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting up the application...")
        await run_migrations()
        async with FileQueueProcessor() as processor:
            await processor.re_process()
        scheduler_thread = Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Application started successfully...")
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        logger.info("Shutting down the application...")
        scheduler.shutdown(wait=True)
        logger.info("Application shutdown complete.")


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ALLOW_ORIGINS", "http://localhost, http://127.0.0.1"
    ).split(", "),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def check_health():
    return {"response": "Service is healthy!"}


app.include_router(api_router, prefix="/api")
