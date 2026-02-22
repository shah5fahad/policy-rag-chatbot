# src/ai/embedding_factory.py

from loguru import logger
from typing import List, Optional

from .model_factory import ModelFactory
from .config import AIModelProvider
from pydantic_ai import Embedder


class EmbeddingFactory:
    """
    Uses pydantic_ai to initialize and dispatch to the correct embedding backend.
    This abstracts away provider-specific dependencies.
    """

    def __init__(self, provider: Optional[AIModelProvider] = None) -> None:
        provider, model_name = ModelFactory.get_model_name(provider=provider, is_embedding=True)
        self.model = Embedder(model=f"{provider.value}:{model_name}")
        self.provider = provider

    async def embed_documents(self, texts: List[str]) -> list[list[float]]:
        logger.info("Embedding start: {} documents using provider '{}'", len(texts), self.provider)
        if not texts:
            raise ValueError("Text list for embedding cannot be empty.")

        # pydantic_ai `AIModel.embed` returns shape [[float]]
        response = await self.model.embed(texts, input_type='document')
        return response.embeddings

    async def embed_query(self, query: str) -> list[float]:
        logger.info("Embedding start : query using provider '{}'", self.provider)
        if not query:
            raise ValueError("Query text cannot be empty.")
        
        if self.provider == AIModelProvider.HUGGINGFACE.value:
            return self.model.encode([query])[0].tolist()

        response = await self.model.embed([query], input_type='query')
        return response.embeddings[0]