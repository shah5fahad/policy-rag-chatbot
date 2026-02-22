# database/configs/_database.py
import os
import threading
from contextlib import asynccontextmanager

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from loguru import logger  # ADD: For better logging

# No user context needed when authentication is disabled


class DatabaseConfig:
    _thread_local = threading.local()

    @classmethod
    def get_engine(cls):
        if not hasattr(cls._thread_local, "engine"):
            database_url = os.getenv("SQLALCHEMY_DATABASE_URI")
            
            # ADD: Default fallback for development
            if not database_url:
                database_url = "sqlite+aiosqlite:///./docparser.db"
                logger.warning(f"No DATABASE_URL found, using default: {database_url}")
            
            # SQLite-specific configuration
            if database_url and "sqlite" in database_url:
                engine = create_async_engine(
                    url=database_url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=os.getenv("SQL_ECHO", "False").lower() == "true",  # ADD: SQL echo setting
                )
                
                # Enable autoincrement support for SQLite
                @event.listens_for(engine.sync_engine, "connect")
                def set_sqlite_pragma(dbapi_conn, connection_record):
                    cursor = dbapi_conn.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA synchronous=NORMAL")  # ADD: Better performance
                    cursor.close()
                    
            else:
                engine = create_async_engine(
                    url=database_url,
                    pool_recycle=1800,
                    pool_size=5,
                    max_overflow=45,
                    pool_pre_ping=True,
                    pool_timeout=60,
                    echo=os.getenv("SQL_ECHO", "False").lower() == "true",  # ADD: SQL echo setting
                )
            
            cls._thread_local.engine = engine
        return cls._thread_local.engine

    @classmethod
    def _get_session_factory(cls):
        if not hasattr(cls._thread_local, "session_factory"):
            cls._thread_local.session_factory = async_sessionmaker(
                bind=cls.get_engine(),
                class_=AsyncSession,  # ADD: Explicitly set class
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
            )
        return cls._thread_local.session_factory

    @classmethod
    @asynccontextmanager
    async def async_session(cls):
        session_factory = cls._get_session_factory()
        async with session_factory() as session:
            # set a default static user context since auth is disabled
            session.info["user"] = os.getenv("DEFAULT_USER", "system")  # IMPROVED: Configurable user
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    # ADD: Health check method
    @classmethod
    async def check_health(cls) -> bool:
        """Check database connection health."""
        try:
            async with cls.async_session() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception:
            return False


async def get_db_session():
    async with DatabaseConfig.async_session() as session:
        yield session