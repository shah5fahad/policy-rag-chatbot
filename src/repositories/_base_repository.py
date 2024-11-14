from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Type, TypeVar

from sqlalchemy import asc, desc
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.future import select

from src.config import DatabaseConfig

T = TypeVar("T")


class BaseRepository:
    def __init__(self, model: Type[T]):
        self._model = model

    @asynccontextmanager
    async def get_session(self):
        async with DatabaseConfig.async_session() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def create(self, **kwargs: Dict[str, Any]):
        async with self.get_session() as session:
            instance = self._model(**kwargs)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def get(self, id: Any):
        async with self.get_session() as session:
            result = await session.get(self._model, id)
            if result is None:
                raise NoResultFound(f"{self._model.__name__} not found with id {id}")
            return result

    async def patch(self, id: Any, **kwargs: Dict[str, Any]):
        async with self.get_session() as session:
            instance = await session.get(self._model, id)
            if not instance:
                raise NoResultFound(f"{self._model.__name__} not found with id {id}")
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def delete(self, id: Any):
        async with self.get_session() as session:
            instance = await session.get(self._model, id)
            if not instance:
                raise NoResultFound(f"{self._model.__name__} not found with id {id}")
            await session.delete(instance)
            await session.commit()
            return True

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        filter_by: Optional[Dict[str, Any]] = {},
        order_by: Optional[Dict[str, str]] = {},
    ):
        async with self.get_session() as session:
            offset = (page - 1) * page_size
            query = (
                select(self._model)
                .filter_by(**filter_by)
                .offset(offset)
                .limit(page_size)
            )
            for field, direction in order_by.items():
                ordering = asc if direction == "asc" else desc
                query = query.order_by(ordering(getattr(self._model, field)))
            result = await session.execute(query)
            return result.scalars().all()

    async def execute(self, query):
        async with self.get_session() as session:
            result = await session.execute(query)
            return result
