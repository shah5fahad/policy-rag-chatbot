import os
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


class DatabaseConfig:
    @classmethod
    def async_engine(cls):
        return create_async_engine(
            os.getenv("SQLALCHEMY_DATABASE_URI"), pool_pre_ping=True, pool_recycle=3600
        )

    @classmethod
    @asynccontextmanager
    async def async_session(cls):
        engine = cls.async_engine()
        session_factory = async_sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        session = session_factory()
        try:
            yield session
        finally:
            await session.close()
            await engine.dispose()
