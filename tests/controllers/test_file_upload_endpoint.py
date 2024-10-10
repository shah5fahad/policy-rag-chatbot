import pytest
import os
import tempfile
import zipfile
from fastapi import UploadFile
from unittest.mock import patch, AsyncMock, ANY
from src.services import FileService
from src.models import FileQueueStatus
from datetime import datetime

@pytest.mark.asyncio
class TestFileController:
    @staticmethod
    def create_temp_pdf():
        """Helper method to create a temporary PDF file."""
        pdf_path = os.path.join(tempfile.gettempdir(), "test.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n% some pdf content")
        return pdf_path

    @pytest.mark.asyncio
    async def test_successful_zip_file_upload(self):
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            with zipfile.ZipFile(tmp, 'w') as zipf:
                pdf_path = self.create_temp_pdf()
                zipf.write(pdf_path, "test.pdf")
            tmp.seek(0)
            zip_file = UploadFile(filename="test.zip", file=tmp)
            mock_timestamp = datetime.now().timestamp()
            mock_s3_folder = f"{mock_timestamp}_{zip_file.filename}"
            mock_file_queue_entry = {
                "email_id": os.getenv("RECIPIENT_EMAIL", "default_email@test.com"),
                "s3_folder_name": mock_s3_folder,
                "id": 63,
                "details": None,
                "status": FileQueueStatus.UPLOADED,
                "created_at": datetime.now().isoformat(),
            }
            with patch("src.repositories.FileQueueRepository.create", new_callable=AsyncMock) as mock_create:
                mock_create.return_value = mock_file_queue_entry
                async with FileService() as service:
                    result = await service.create(zip_file=zip_file, email_id=os.getenv("RECIPIENT_EMAIL", "default_email@test.com"))
                assert result["email_id"] == os.getenv("RECIPIENT_EMAIL", "default_email@test.com")
                assert isinstance(result["id"], int)
                assert result["status"] == FileQueueStatus.UPLOADED
                assert "created_at" in result
                mock_create.assert_awaited_once_with(
                    s3_folder_name=ANY, 
                    email_id=os.getenv("RECIPIENT_EMAIL", "default_email@test.com"),
                    status=FileQueueStatus.UPLOADED
                )
        os.remove(tmp.name)

    @pytest.mark.asyncio
    async def test_upload_non_zip_file(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"Not a zip file content")
            tmp.seek(0)
            non_zip_file = UploadFile(filename="test.txt", file=tmp)
            async with FileService() as service:
                with pytest.raises(ValueError, match="Uploaded file is not a zip file"):
                    await service.create(zip_file=non_zip_file, email_id="test@example.com")
        os.remove(tmp.name)

    @pytest.mark.asyncio
    async def test_upload_zip_with_non_pdf_files(self):
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            with zipfile.ZipFile(tmp, 'w') as zipf:
                txt_path = os.path.join(tempfile.gettempdir(), "test.txt")
                with open(txt_path, "w") as f:
                    f.write("This is not a PDF file")
                zipf.write(txt_path, "test.txt")
            tmp.seek(0)
            zip_file = UploadFile(filename="test.zip", file=tmp)
            async with FileService() as service:
                with pytest.raises(ValueError, match="Uploaded zip file contains non-PDF files"):
                    await service.create(zip_file=zip_file, email_id="test@example.com")
        os.remove(tmp.name)

    @pytest.mark.asyncio
    async def test_empty_zip_file(self):
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            with zipfile.ZipFile(tmp, 'w') as zipf:
                pass 
            tmp.seek(0)
            zip_file = UploadFile(filename="test.zip", file=tmp)
            async with FileService() as service:
                with pytest.raises(ValueError, match="Uploaded zip file is empty"):
                    await service.create(zip_file=zip_file, email_id="test@example.com")
        os.remove(tmp.name)
