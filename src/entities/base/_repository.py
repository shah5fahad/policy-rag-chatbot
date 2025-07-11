from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import asc, desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.sql import Select
from sqlmodel import SQLModel

from src.configs import DatabaseConfig

ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseRepository:
    def __init__(self, model: Type[ModelT]):
        self.model = model

    @asynccontextmanager
    async def get_session(self):
        async with DatabaseConfig.async_session() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def create(self, object: ModelT):
        object.id = None  # Ensure the ID is set to None for new objects
        async with self.get_session() as session:
            session.add(object)
            await session.commit()
            await session.refresh(object)
            return object

    async def upsert(self, object: ModelT):
        async with self.get_session() as session:
            instance = await session.get(self.model, object.id)
            if not instance:
                object.id = None  # Ensure the ID is set to None for new objects
                instance = object
                session.add(instance)
            else:
                for key, value in object.model_dump().items():
                    if key not in self.model.__fields__:
                        raise SQLAlchemyError(f"Invalid field: {key}")
                    setattr(instance, key, value)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def list(
        self,
        page: int = 1,
        page_size: int = 10,
        order_by: Optional[List[str]] = None,
        filter_by: Optional[Dict[str, Any]] = None,
    ):
        filter_by = {
            k: v for k, v in (filter_by or {}).items() if k in self.model.__fields__
        }
        order_by = [
            field
            for field in (order_by or [])
            if field.lstrip("-") in self.model.__fields__
        ]
        offset: int = (page - 1) * page_size
        async with self.get_session() as session:
            query: Select[Any] = (
                select(self.model)
                .filter_by(**filter_by)
                .offset(offset)
                .limit(page_size)
            )
            for field in order_by:
                if field.startswith("-"):
                    query = query.order_by(desc(getattr(self.model, field[1:])))
                else:
                    query = query.order_by(asc(getattr(self.model, field)))
            result = await session.execute(query)
            return [item for item in result.scalars().all()]

    async def get(self, id: Any):
        async with self.get_session() as session:
            result = await session.get(self.model, id)
            return result

    async def patch(self, id: Any, **kwargs: Dict[str, Any]):
        async with self.get_session() as session:
            instance = await session.get(self.model, id)
            if not instance:
                raise SQLAlchemyError(f"{self.model.__name__} not found with id {id}")
            for key, value in kwargs.items():
                if key not in self.model.__fields__:
                    raise SQLAlchemyError(f"Invalid field: {key}")
                setattr(instance, key, value)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def delete(self, id: Any):
        async with self.get_session() as session:
            instance = await session.get(self.model, id)
            if not instance:
                raise SQLAlchemyError(f"{self.model.__name__} not found with id {id}")
            await session.delete(instance)
            await session.commit()

    async def count(self, filter_by: Optional[Dict[str, Any]] = None):
        filter_by = {
            k: v for k, v in (filter_by or {}).items() if k in self.model.__fields__
        }
        async with self.get_session() as session:
            query: Select[Any] = (
                select(func.count()).select_from(self.model).filter_by(**filter_by)
            )
            result = await session.execute(query)
            return result.scalar_one() or 0

    async def execute(self, query: Any):
        async with self.get_session() as session:
            result = await session.execute(query)
            return result
