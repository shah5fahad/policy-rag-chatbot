from typing import List, Optional, Dict, Any
from uuid import uuid4

import chromadb
from chromadb.config import Settings
from loguru import logger

from .config import AISettings


class ChromaVectorStore:
    """
    Production-grade Chroma vector store wrapper.

    Features:
    - Persistent storage
    - Safe document insertion
    - Unique ID generation
    - Structured search results
    - Logging via loguru
    """

    def __init__(self, collection_name: str = "default"):
        self.collection_name = collection_name

        try:
            logger.info("Initializing Chroma client at {}", AISettings.CHROMA_PATH)

            self.client = chromadb.Client(
                Settings(
                    persist_directory=AISettings.CHROMA_PATH,
                    is_persistent=True,
                )
            )

            self.collection = self.client.get_or_create_collection(
                name=collection_name
            )

            logger.success("Chroma collection ready: {}", collection_name)

        except Exception:
            logger.exception("Failed to initialize Chroma vector store")
            raise

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:

        if not documents:
            logger.warning("No documents provided for insertion")
            return

        if len(documents) != len(embeddings):
            raise ValueError("Documents and embeddings length mismatch")

        if metadatas and len(metadatas) != len(documents):
            raise ValueError("Metadatas length must match documents")

        try:
            ids = [str(uuid4()) for _ in documents]

            logger.debug("Adding {} documents to Chroma", len(documents))

            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas or [{} for _ in documents],
                ids=ids,
            )

            self.client.persist()

            logger.success("Inserted {} documents into {}", len(documents), self.collection_name)

        except Exception:
            logger.exception("Failed to add documents to Chroma")
            raise

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:

        if not query_embedding:
            raise ValueError("Query embedding is empty")

        try:
            logger.debug("Searching Chroma | top_k={}", top_k)

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )

            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            structured_results = []

            for doc, meta, distance in zip(documents, metadatas, distances):
                structured_results.append(
                    {
                        "document": doc,
                        "metadata": meta,
                        "score": 1 - distance if distance is not None else None,
                    }
                )

            logger.debug("Search returned {} results", len(structured_results))
            return structured_results

        except Exception:
            logger.exception("Chroma search failed")
            raise