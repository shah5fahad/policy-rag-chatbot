import re
from sqlalchemy import select

from src.models import FileQueue

from ._base_repository import BaseRepository


class FileQueueRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=FileQueue)

    async def get_oldest_queue_with_status(self, status: str, limit: int = 1):
        async with self.get_session() as session:
            query = (
                select(FileQueue)
                .where(FileQueue.status == status)
                .order_by(FileQueue.created_at.asc())
                .limit(limit)
            )
            result = await session.execute(query)
            result = result.scalar()
            return result

    async def bulk_update_status(self, existing_status: str, new_status: str):
        async with self.get_session() as session:
            query = (
                select(FileQueue)
                .where(FileQueue.status == existing_status)
                .order_by(FileQueue.created_at.desc())
            )
            result = await session.execute(query)
            queues = result.scalars().all()
            if queues:
                for queue in queues:
                    queue.status = new_status
                await session.commit()
        return queues
