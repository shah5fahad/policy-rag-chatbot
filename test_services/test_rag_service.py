# tests/test_rag_service.py

import sys, asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent  # Goes up from test_services/ to fastapi/
sys.path.insert(0, str(project_root))

from src.ai_services.rag_service import RAGService
from src.ai_services.config import AIModelProvider


async def run_test_rag_service():
    """
    Test the RAGService end-to-end:
    1. Index a few documents
    2. Query the system
    3. Print the answer
    """
    rag = RAGService(
        collection_name="books"
    )

    # Index documents
    await rag.index_documents(
        documents=[
            "FastAPI is a modern web framework for building APIs with Python.",
            "FastAPI is built on top of Starlette and Pydantic, providing high performance and easy data validation.",
            "Gemini is a conversational AI model developed by Google.",
        ],
        metadatas=[
            {"source": "doc1"},
            {"source": "doc2"},
            {"source": "doc3"},
        ]
    )

    # Query
    question = "What is FastAPI?"
    result = await rag.query(question)

    print(f"Question: {question}")
    print(f"Answer: {result.answer}")


if __name__ == "__main__":
    asyncio.run(run_test_rag_service())