from fastapi import Body, UploadFile, File, BackgroundTasks, HTTPException, Request
from fastapi.responses import Response
import os
import shutil
from loguru import logger
from src.ai_services.config import AIModelProvider
from ._model import ProcessingStatus
from ..base import BaseController
from ._schema import DocumentSchema, DocumentCreateSchema, DocumentUpdateSchema, DocumentStatusSchema
from ._service import DocumentService
from src.utils.document_processing_service import DocumentProcessingService
from src.ai_services.rag_service import RAGService
from datetime import datetime
from  dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


class DocumentController(BaseController):
    def __init__(self):
        super().__init__(DocumentService)
        
        # Add custom routes
        self.router.add_api_route(
            "/upload",
            self.upload,
            methods=["POST"],
            tags=["Documents"]
        )
        self.router.add_api_route(
            "/stats/",
            self.get_stats,
            methods=["GET"],
            tags=["Stats"]
        )
        self.router.add_api_route(
            "/{id}/status",
            self.get_status,
            methods=["GET"],
            tags=["Documents", "Status"]
        )
        self.router.add_api_route(
            "/filter_by_status/",
            self.get_filter_by_status,
            methods=["GET"],
            tags=["Documents Status"]
        )
        self.router.add_api_route(
            "/{id}/complete",
            self.mark_completed,
            methods=["POST"],
            tags=["Documents", "Completion"]
        )
        self.router.add_api_route(
            "/{id}/fail",
            self.mark_failed,
            methods=["POST"],
            tags=["Documents", "Failure"]
        )
        self.router.add_api_route(
            "/{id}/process",
            self.trigger_processing,
            methods=["POST"],
            tags=["Documents", "Processing"]
        )
        self.router.add_api_route(
            "/query/",
            self.query_documents,
            methods=["POST"],
            tags=["Documents", "Query"]
        )
    
    async def create(self, data: DocumentCreateSchema = Body(...)):
        """Create a new document record."""
        return await super().create(data.model_dump())
    
    async def patch(self, id: int, data: DocumentUpdateSchema = Body(...)):
        """Update document."""
        return await super().patch(id, data.model_dump(exclude_unset=True))
    
    async def upload(
        self, 
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...)
    ):
        """Upload a document file and trigger background processing."""
        # Validate file type
        allowed_types = ["pdf", "txt", "md", "docx"]
        file_ext = file.filename.split(".")[-1].lower()
        
        if file_ext not in allowed_types:
            return Response(status_code=400, content=f"File type .{file_ext} not allowed")
        
        # Save file
        upload_dir = os.getenv("DOCUMENT_UPLOAD_DIR", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        try:
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create document record
            document = await self.service.create_document(
                filename=file.filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                mime_type=file.content_type or "application/octet-stream",
                document_type=file_ext
            )
            
            # Add background task to process document
            background_tasks.add_task(
                self._process_document_background,
                document_id=document.id
            )
            
            return Response(status_code=201, content=f"Document uploaded successfully. Processing started in background.")
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return Response(status_code=500, content=f"Upload failed: {str(e)}")
    
    async def _process_document_background(self, document_id: int):
        """Background task to process document."""
        try:
            # Initialize services
            rag_service = RAGService(
                collection_name=os.getenv("VECTOR_COLLECTION_NAME", "documents"),
                provider=AIModelProvider.GEMINI  # or from settings
            )
            processing_service = DocumentProcessingService(rag_service)
            
            # Process document
            result = await processing_service.process_document(document_id)
            
            if result["success"]:
                logger.info(f"Background processing completed for document {document_id}")
            else:
                logger.error(f"Background processing failed for document {document_id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Background processing error for document {document_id}: {e}")
    
    async def trigger_processing(self, id: int, background_tasks: BackgroundTasks):
        """Manually trigger processing for a document."""
        document = await self.service.get(id)
        
        if not document:
            return Response(status_code=404, content="Document not found")
        
        if document.status == ProcessingStatus.PROCESSING:
            return Response(status_code=400, content="Document is already being processed")
        
        # Add to background tasks
        background_tasks.add_task(
            self._process_document_background,
            document_id=id
        )
        return Response(status_code=200, content="Document processing triggered in background")

    async def query_documents(self, question: str = Body(..., embed=True)):
        """
        Query the RAG system with a question.
        
        Args:
            question: The question to ask
        """
        try:
            # Initialize RAG service
            rag_service = RAGService(
                collection_name=os.getenv("VECTOR_COLLECTION_NAME", "documents"),
                provider=AIModelProvider.GEMINI
            )
            
            # Query
            result = await rag_service.query(question)
            print(f"RAG Query Result: {result} {question}")  # Debug log
            return {
                "status": "success",
                "question": question,
                "answer": result.answer,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return Response(status_code=500, content=f"Query failed: {str(e)}")

    async def get_status(self, id: int):
        """Get document processing status."""
        status = await self.service.get_document_status(id)
        if not status:
            raise HTTPException(status_code=404, detail="Document not found")
        return status
    
    async def get_stats(self):
        """Get document processing stats."""
        stats = await self.service.get_document_stats()
        return stats

    async def get_filter_by_status(self, request: Request):
        """
        Get documents filtered by status using query parameter.
        Example:
        /documents/status?status=pending
        """
        try:
            status = request.query_params.get("status")
            if not status:
                raise HTTPException(status_code=400, detail="Missing 'status' query parameter")
            try:
                status_enum: ProcessingStatus = ProcessingStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status value: {status}")
            
            documents = await self.service.get_by_status(status_enum)
            return documents
        except HTTPException as e:
            logger.warning(e)
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching documents by status: {str(e)}"
            )
    
    async def mark_completed(self, id: int):
        """Mark document as completed."""
        document = await self.service.mark_as_completed(id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    
    async def mark_failed(self, id: int, error: str = Body(..., embed=True)):
        """Mark document as failed."""
        document = await self.service.mark_as_failed(id, error)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document