import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.document_processing_service import DocumentProcessingService
from src.entities.document._service import DocumentService
from src.ai_services.rag_service import RAGService
from src.ai_services.config import AIModelProvider


async def test_document_processing():
    """Test the complete document processing flow."""
    
    # Create a test document record
    doc_service = DocumentService()
    document = await doc_service.create_document(
        filename="test.md",
        file_path="uploads/test.md",
        file_size=100,
        mime_type="text/plain",
        document_type="md"
    )
    
    print(f"Created document with ID: {document.id}")
    
    # Initialize processing service
    rag_service = RAGService(
        collection_name="test_docs",
        provider=AIModelProvider.GEMINI
    )
    processor = DocumentProcessingService(rag_service)
    
    # Process document (this will fail because file doesn't exist)
    # In real test, you'd have a real file
    result = await processor.process_document(document.id)
    
    print(f"Processing result: {result}")
    
    # Test query
    query_result = await rag_service.query("What is the content?")
    print(f"Query result: {query_result.answer}")


if __name__ == "__main__":
    asyncio.run(test_document_processing())