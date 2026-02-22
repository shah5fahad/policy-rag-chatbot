# src/ai/rag_service.py

from typing import List, Optional, Dict, Any
from .config import AIModelProvider
from loguru import logger
from pydantic import BaseModel, Field
from .embedding_factory import EmbeddingFactory
from .vector_store import FAISSVectorStore
from .agent_manager import AgentManager
from .prompts import SYSTEM_PROMPT_ANSWER


# class ReferenceDocument(BaseModel):
#     """Model for reference document information"""
#     content: str = Field(description="The content of the referenced document")
#     metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata of the referenced document")
#     score: Optional[float] = Field(default=None, description="Similarity score from vector search")
#     source: Optional[str] = Field(default=None, description="Source identifier (filename, URL, etc.)")

class AnswerOutput(BaseModel):
    answer: str = Field(description="The generated answer to the user's question")
    
    # references: List[ReferenceDocument] = Field(
    #     default_factory=list, 
    #     description="List of reference documents file name used to generate the answer"
    # )
    # has_references: bool = Field(default=False, description="Whether references were used")


class RAGService:
    """
    Retrieval-Augmented Generation (RAG) service.
    Handles document indexing, vector search, and LLM-based question answering.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        provider: Optional[AIModelProvider] = None,
    ):
        self.provider = provider
        self.embedding_service = EmbeddingFactory(provider)
        self.vector_store = FAISSVectorStore(collection_name)

    async def index_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
    ) -> None:
        """
        Embed and index a list of documents into the vector store.
        """
        if not documents:
            logger.warning("No documents provided for indexing.")
            return

        logger.info("Generating embeddings for {} documents.", len(documents))
        embeddings = await self.embedding_service.embed_documents(documents)

        logger.info("Adding documents to vector store: {}", self.vector_store.collection_name)
        self.vector_store.add_documents(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
    
    async def query(self, question: str, top_k: int = 5) -> AnswerOutput:
        """
        Query the RAG system with a question and get an LLM-generated answer.
        
        Args:
            question: The user's question
            top_k: Number of relevant documents to retrieve
            
        Returns:
            AnswerOutput with the generated answer
        """
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        logger.info("Generating embedding for query: {}", question)
        query_embedding = await self.embedding_service.embed_query(question)

        logger.info("Searching vector store: {} (top_k={})", self.vector_store.collection_name, top_k)
        
        # FIX: Get search results with scores
        search_results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )
        
        # Extract just the document texts for context
        context_docs = [result["document"] for result in search_results]
        
        # Optional: Log scores for debugging
        if search_results:
            scores = [result["score"] for result in search_results]
            logger.debug("Retrieved documents with scores: {}", scores)

        # Create context from retrieved documents
        context = "\n\n---\n\n".join(context_docs)
        
        # Format system prompt with context
        system_prompt = SYSTEM_PROMPT_ANSWER.format(context=context)

        logger.info("Creating agent for question answering.")
        agent = AgentManager.create_agent(
            system_prompt=system_prompt,
            output_type=AnswerOutput,
            provider=self.provider,
            is_embedding=False
        )

        logger.info("Running agent with backoff.")
        response = await AgentManager.run_with_backoff(agent, question)

        return response.output