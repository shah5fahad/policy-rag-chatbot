from typing import Any, Dict, List, Optional, Type, TypeVar

from ._repository import BaseRepository

RepositoryT = TypeVar("RepositoryT", bound="BaseRepository")


class BaseService:
    def __init__(self, repository: Type[RepositoryT]):
        self.repository = repository()

    async def create(self, data: Dict[str, Any]):
        return await self.repository.create(object=self.repository.model(**data))

    async def list(
        self,
        page: int = 1,
        page_size: int = 10,
        order_by: Optional[List[str]] | None = None,
        filter_by: Dict[str, Any] | None = None,
    ):
        return await self.repository.list(
            page=page,
            page_size=page_size,
            filter_by=filter_by,
            order_by=order_by,
        )

    async def get(self, id: int):
        return await self.repository.get(id=id)

    async def patch(self, id: int, data: Dict[str, Any]):
        return await self.repository.patch(id=id, **data)

    async def delete(self, id: int):
        return await self.repository.delete(id=id)

    async def count(self, filter_by: Dict[str, Any] | None = None):
        return await self.repository.count(filter_by=filter_by)
