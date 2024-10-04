from fastapi import APIRouter, HTTPException, UploadFile

from src.services import FileService
from src.utils import logger


class FileController:
    def __init__(self):
        self.service = FileService
        self.router = APIRouter(prefix="/files", tags=["File"])
        self.router.add_api_route("/", self.create, methods=["POST"])

    async def create(self, zip_file: UploadFile):
        logger.info(
            f"Received request to analyze files for zip file: {zip_file.filename}"
        )
        try:
            async with self.service() as service:
                user = await service.create(
                    zip_file=zip_file, email_id="RECIPIENT_EMAIL"
                )
                return user
        except HTTPException as e:
            logger.warning(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail=str(e))
