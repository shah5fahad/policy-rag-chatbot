from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import asc, desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.sql import Select

from src.configs import DatabaseConfig

from ._model import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository:
    def __init__(self, model: Type[ModelT]):
        self.model = model

    @asynccontextmanager
    async def get_session(self):
        async with DatabaseConfig.async_session() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                try:
                    await session.rollback()
                except Exception as e2:
                    print(f"Rollback failed: {e2}")
                raise e

    async def create(self, object: ModelT):
        async with self.get_session() as session:
            session.add(object)
            await session.commit()
            await session.refresh(object)
            return object

    async def upsert(self, object: ModelT):
        async with self.get_session() as session:
            instance = await session.get(self.model, object.id)
            if not instance:
                instance = object
                session.add(instance)
            else:
                column_names = [c.key for c in self.model.__table__.columns]
                for key, value in object.__dict__.items():
                    if key.startswith("_"):
                        continue
                    if key not in column_names:
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
        column_names = [c.key for c in self.model.__table__.columns]
        filter_by = {k: v for k, v in (filter_by or {}).items() if k in column_names}
        order_by = [
            field for field in (order_by or []) if field.lstrip("-") in column_names
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
            column_names = [c.key for c in self.model.__table__.columns]
            for key, value in kwargs.items():
                if key not in column_names:
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
        column_names = [c.key for c in self.model.__table__.columns]
        filter_by = {k: v for k, v in (filter_by or {}).items() if k in column_names}
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
