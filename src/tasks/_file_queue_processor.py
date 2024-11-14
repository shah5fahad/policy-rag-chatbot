import json
import tempfile

from src.config import logger
from src.models import FileQueue, FileQueueStatus
from src.repositories import FileQueueRepository
from src.utils import OpenAIClient


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
            logger.info(f"Processing file: {oldest_queue.s3_folder_name}")
            context = "ABC"
            final_response = {}
            response = ""
            messages = [{"role": "user", "content": context}]
            async with OpenAIClient(instruction_no=0) as openai_client:
                async for chunk in openai_client.create_chat_completions(
                    messages=messages
                ):
                    response += chunk
            data = json.loads(response)
            final_response.update(data)
            response = ""
            async with OpenAIClient(instruction_no=1) as openai_client:
                async for chunk in openai_client.create_chat_completions(
                    messages=messages
                ):
                    response += chunk
            data = json.loads(response)
            final_response.update(data)
            response = ""
            async with OpenAIClient(instruction_no=2) as openai_client:
                async for chunk in openai_client.create_chat_completions(
                    messages=messages
                ):
                    response += chunk
            data = json.loads(response)
            final_response.update(data)
            with tempfile.TemporaryDirectory() as directory:
                await self.file_queue_repository.patch(
                    id=oldest_queue.id,
                    status=FileQueueStatus.COMPLETED,
                    details=f"File has been processed and sent to the user via email. The link to download the file is",
                )
            logger.info(f"Processed file: {oldest_queue.s3_folder_name}")
        except Exception as e:
            logger.exception(f"Error processing file: {e}")
        finally:
            pass
