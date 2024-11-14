import os
import tempfile
import zipfile
from datetime import datetime

import filetype
from fastapi import HTTPException, UploadFile

from src.models import FileQueueStatus
from src.repositories import FileQueueRepository


class FileService:
    def __init__(self):
        self.file_queue_repository = FileQueueRepository()

    async def create(self, zip_file: UploadFile, email_id: str):
        destination = f"{datetime.now().timestamp()}_{zip_file.filename}"
        if not zipfile.is_zipfile(zip_file.file):
            raise HTTPException(
                status_code=400, detail="Uploaded file is not a zip file"
            )
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_file.file, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            if not os.listdir(temp_dir):
                raise HTTPException(
                    status_code=400, detail="Uploaded zip file is empty"
                )
            for root, dirs, files in os.walk(temp_dir):
                if dirs:
                    for d in dirs:
                        os.rmdir(os.path.join(root, d))
                for file in files:
                    file_path = os.path.join(root, file)
                    file_type = filetype.guess(file_path)
                    if not file_type or not file_type.extension == "pdf":
                        raise HTTPException(
                            status_code=400,
                            detail="Uploaded zip file contains non-PDF files",
                        )
        return await self.file_queue_repository.create(
            s3_folder_name=destination,
            email_id=email_id,
            status=FileQueueStatus.UPLOADED,
        )
