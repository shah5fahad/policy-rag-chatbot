from contextlib import asynccontextmanager

from sqlalchemy.future import select

from src.config import DatabaseConfig


class BaseRepository:
    def __init__(self, model=None):
        self.__model = model
        assert self.__model is not None, "model must be defined"

    @asynccontextmanager
    async def get_session(self):
        async with DatabaseConfig.async_session() as session:
            yield session

    async def create(self, **kwargs: dict):
        async with self.get_session() as session:
            instance = self.__model(**kwargs)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        filter_by: dict = {},
        order_by: dict = {},
    ):
        async with self.get_session() as session:
            offset = (page - 1) * page_size
            query = select(self.__model).offset(offset).limit(page_size)
            query = query.filter_by(**filter_by)
            for field, direction in order_by.items():
                if direction == "asc":
                    query = query.order_by(getattr(self.__model, field).asc())
                elif direction == "desc":
                    query = query.order_by(getattr(self.__model, field).desc())
            result = await session.execute(query)
            return [row for row in result.scalars()]

    async def get(self, id):
        async with self.get_session() as session:
            query = select(self.__model).where(self.__model.id == id)
            result = await session.execute(query)
            result = result.scalar()
            if result:
                return result

    async def patch(self, id, **kwargs: dict):
        async with self.get_session() as session:
            instance = await session.get(self.__model, id)
            if not instance:
                raise Exception(f"{self.__model.__name__} not found with id {id}")
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def delete(self, id):
        async with self.get_session() as session:
            instance = await session.get(self.__model, id)
            if not instance:
                raise Exception(f"{self.__model.__name__} not found with id {id}")
            await session.delete(instance)
            await session.commit()
            return True
