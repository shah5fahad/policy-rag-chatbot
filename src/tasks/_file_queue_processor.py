from loguru import logger

from src.models import FileQueue, FileQueueStatus
from src.repositories import FileQueueRepository


class FileQueueProcessor:
    def __init__(self):
        self.file_queue_repository = FileQueueRepository()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def re_process(self):
        await self.file_queue_repository.bulk_update_status(
            existing_status=FileQueueStatus.PROCESSING,
            new_status=FileQueueStatus.UPLOADED,
        )

    async def process(self):
        oldest_queue: FileQueue = (
            await self.file_queue_repository.get_oldest_queue_with_status(
                status=FileQueueStatus.UPLOADED, limit=1
            )
        )
        if not oldest_queue:
            logger.info("No files to process")
            return
        try:
            await self.file_queue_repository.patch(
                id=oldest_queue.id, status=FileQueueStatus.PROCESSING
            )
        except Exception as e:
            logger.exception(e)
