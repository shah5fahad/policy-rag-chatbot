from typing import Optional, Dict, Any, List
from src.ai_services.rag_service import RAGService
from src.ai_services.config import AIModelProvider
from src.entities.document._model import ProcessingStatus
from src.entities.document._service import DocumentService
from .document_parser import ParserFactory
from loguru import logger
from dotenv import load_dotenv
import os


load_dotenv()  # Load environment variables from .env file

class DocumentProcessingService:
    """Service to process documents and integrate with RAG."""
    
    def __init__(self, rag_service: Optional[RAGService] = None):
        self.rag_service = rag_service or RAGService(
            collection_name=os.getenv("VECTOR_COLLECTION_NAME", "documents"),
            provider=AIModelProvider.GEMINI
        )
        self.document_service = DocumentService()
        self.parser_factory = ParserFactory()
    
    async def process_document(self, document_id: int) -> Dict[str, Any]:
        """
        Process a document: parse content, generate embeddings, index in RAG.
        
        Args:
            document_id: ID of the document to process
            
        Returns:
            Processing result dictionary
        """
        logger.info(f"Starting processing for document ID: {document_id}")
        
        # Get document from database
        document = await self.document_service.get(document_id)
        if not document:
            error_msg = f"Document with ID {document_id} not found"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # Update status to PROCESSING
            await self.document_service.mark_as_processing(document_id)
            
            # Get appropriate parser
            parser = self.parser_factory.get_parser(document.document_type)
            if not parser:
                error_msg = f"No parser available for file type: {document.document_type}"
                logger.error(error_msg)
                await self.document_service.mark_as_failed(document_id, error_msg)
                return {"success": False, "error": error_msg}
            
            # Parse document
            logger.info(f"Parsing document: {document.filename}")
            parsed_content = await parser.parse(document.file_path)
            
            # Check if we got any text
            if not parsed_content.get("text") or not parsed_content["text"].strip():
                warning_msg = "No text content extracted from document"
                logger.warning(warning_msg)
                await self.document_service.mark_as_failed(document_id, warning_msg)
                return {"success": False, "error": warning_msg}
            
            # Prepare documents and metadata for RAG
            chunks = parsed_content.get("chunks", [])
            if not chunks:
                # If no chunks, use the whole text as one chunk
                chunks = [parsed_content["text"]]
            
            # Create metadata for each chunk
            metadatas = []
            for i, chunk in enumerate(chunks):
                metadatas.append({
                    "document_id": document_id,
                    "filename": document.filename,
                    "chunk_index": i,
                    "source": document.file_path,
                    **parsed_content.get("metadata", {})
                })
                
            #Update document metadata in database
            await self.document_service.update_document_metadata(document_id, metadatas)
            
            # Index in RAG service
            logger.info(f"Indexing {len(chunks)} chunks in RAG for document: {document.filename}")
            await self.rag_service.index_documents(
                documents=chunks,
                metadatas=metadatas
            )
            
            # Update document as COMPLETED
            await self.document_service.mark_as_completed(document_id)
            
            logger.success(f"Document {document_id} processed successfully")
            
            return {
                "success": True,
                "document_id": document_id,
                "chunks_processed": len(chunks),
                "text_length": len(parsed_content["text"]),
                "metadata": parsed_content.get("metadata", {})
            }
            
        except Exception as e:
            error_msg = f"Document processing failed: {str(e)}"
            logger.error(error_msg)
            await self.document_service.mark_as_failed(document_id, error_msg)
            return {"success": False, "error": error_msg}
    
    async def reprocess_failed_documents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Reprocess documents that failed.
        
        Args:
            limit: Maximum number of documents to reprocess
            
        Returns:
            List of processing results
        """
        failed_docs = await self.document_service.get_by_status(ProcessingStatus.FAILED, limit)
        results = []
        
        for doc in failed_docs:
            result = await self.process_document(doc.id)
            results.append(result)
        
        return results