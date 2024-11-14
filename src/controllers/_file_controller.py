from fastapi import APIRouter, HTTPException, UploadFile

from src.services import FileService
from src.utils import logger


class FileController:
    def __init__(self):
        self.__file_service = FileService()
        self.router = APIRouter()
        self.router.add_api_route("/", self.create, methods=["POST"])

    async def create(self, zip_file: UploadFile):
        try:
            file = await self.__file_service.create(
                zip_file=zip_file, email_id="RECIPIENT_EMAIL"
            )
            return file
        except HTTPException as e:
            logger.warning(e)
            raise e
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=500, detail=str(e))
