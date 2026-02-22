# src/ai_services/vector_store.py

from typing import List, Optional, Dict, Any, Tuple
from uuid import uuid4
import os
import pickle
import numpy as np
import faiss
from loguru import logger
from dataclasses import dataclass, field
from .config import AISettings


@dataclass
class Document:
    """Document class for storing text, metadata, and embedding."""
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    id: str = field(default_factory=lambda: str(uuid4()))


class FAISSVectorStore:
    """
    Production-grade FAISS vector store wrapper.
    
    Features:
    - Persistent storage
    - Safe document insertion
    - Unique ID generation
    - Structured search results with scores
    - Logging via loguru
    - Cosine similarity search
    """

    def __init__(self, collection_name: str = "default"):
        self.collection_name = collection_name
        self.persist_directory = AISettings.VECTOR_STORE_PATH
        self.index_path = os.path.join(self.persist_directory, f"{collection_name}.faiss")
        self.metadata_path = os.path.join(self.persist_directory, f"{collection_name}.pkl")

        try:
            logger.info("Initializing FAISS vector store at {}", self.persist_directory)

            # Create directory if it doesn't exist
            os.makedirs(self.persist_directory, exist_ok=True)

            # Initialize index and documents
            self.index: Optional[faiss.Index] = None
            self.documents: List[Document] = []
            self.dimension: Optional[int] = None

            # Load existing index if available
            self._load()

            logger.success("FAISS vector store ready: {}", collection_name)

        except Exception:
            logger.exception("Failed to initialize FAISS vector store")
            raise

    def _load(self) -> None:
        """Load existing index and documents from disk."""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                # Load FAISS index
                self.index = faiss.read_index(self.index_path)
                
                # Load documents metadata
                with open(self.metadata_path, 'rb') as f:
                    self.documents = pickle.load(f)
                
                if self.documents:
                    self.dimension = self.index.d
                
                logger.info("Loaded existing index with {} documents", len(self.documents))
            else:
                logger.info("No existing index found, starting fresh")
                
        except Exception as e:
            logger.error("Failed to load existing index: {}", e)
            # Start fresh if load fails
            self.index = None
            self.documents = []

    def _save(self) -> None:
        """Save index and documents to disk."""
        try:
            if self.index is not None:
                # Save FAISS index
                faiss.write_index(self.index, self.index_path)
                
                # Save documents metadata
                with open(self.metadata_path, 'wb') as f:
                    pickle.dump(self.documents, f)
                
                logger.debug("Saved index with {} documents", len(self.documents))
        except Exception as e:
            logger.error("Failed to save index: {}", e)
            raise

    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """L2 normalize vectors for cosine similarity."""
        faiss.normalize_L2(vectors)
        return vectors

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dicts
            
        Returns:
            List of generated document IDs
        """
        if not documents:
            logger.warning("No documents provided for insertion")
            return []

        if len(documents) != len(embeddings):
            raise ValueError(f"Documents and embeddings length mismatch: {len(documents)} vs {len(embeddings)}")

        if metadatas and len(metadatas) != len(documents):
            raise ValueError(f"Metadatas length must match documents: {len(metadatas)} vs {len(documents)}")

        try:
            # Generate IDs for new documents
            ids = [str(uuid4()) for _ in documents]
            
            # Convert embeddings to numpy array
            embeddings_array = np.array(embeddings).astype('float32')
            current_dim = embeddings_array.shape[1]

            logger.debug("Adding {} documents to FAISS (dim={})", len(documents), current_dim)

            # Initialize index if needed
            if self.index is None:
                self.dimension = current_dim
                # Using IndexFlatIP for inner product (cosine similarity after normalization)
                self.index = faiss.IndexFlatIP(self.dimension)
                logger.info("Created new FAISS index with dimension {}", self.dimension)

            # Verify dimension consistency
            if current_dim != self.dimension:
                raise ValueError(
                    f"Embedding dimension mismatch: expected {self.dimension}, got {current_dim}"
                )

            # Normalize vectors for cosine similarity
            normalized_vectors = self._normalize_vectors(embeddings_array)

            # Add to index
            self.index.add(normalized_vectors)

            # Create and store document objects
            for i, (text, embedding) in enumerate(zip(documents, embeddings)):
                metadata = metadatas[i] if metadatas else {}
                doc = Document(
                    id=ids[i],
                    text=text,
                    metadata=metadata,
                    embedding=embedding  # Store original embedding
                )
                self.documents.append(doc)

            # Save to disk
            self._save()

            logger.success("Inserted {} documents into {}", len(documents), self.collection_name)
            
            return ids

        except Exception:
            logger.exception("Failed to add documents to FAISS")
            raise

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        include_embeddings: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            include_embeddings: Whether to include embeddings in results
            
        Returns:
            List of result dictionaries with document, metadata, and score
        """
        if not query_embedding:
            raise ValueError("Query embedding is empty")

        if self.index is None or self.index.ntotal == 0:
            logger.warning("No documents in index to search")
            return []

        try:
            logger.debug("Searching FAISS | top_k={}", top_k)

            # Convert query to numpy array and normalize
            query_array = np.array([query_embedding]).astype('float32')
            
            # Verify dimension
            if query_array.shape[1] != self.dimension:
                raise ValueError(
                    f"Query dimension mismatch: expected {self.dimension}, got {query_array.shape[1]}"
                )
            
            # Normalize query vector
            query_normalized = self._normalize_vectors(query_array)

            # Search (k cannot exceed total number of vectors)
            k = min(top_k, self.index.ntotal)
            scores, indices = self.index.search(query_normalized, k)

            # Prepare results
            structured_results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1 and idx < len(self.documents):
                    doc = self.documents[idx]
                    result = {
                        "id": doc.id,
                        "document": doc.text,
                        "metadata": doc.metadata,
                        "score": float(score),  # Cosine similarity score
                    }
                    if include_embeddings and doc.embedding:
                        result["embedding"] = doc.embedding
                    
                    structured_results.append(result)

            logger.debug("Search returned {} results", len(structured_results))
            return structured_results

        except Exception:
            logger.exception("FAISS search failed")
            raise

    def search_with_scores(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Search and return only document texts with scores.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (document_text, score) tuples
        """
        results = self.search(query_embedding, top_k)
        return [(r["document"], r["score"]) for r in results]

    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by ID.
        
        Note: FAISS doesn't support direct deletion. This rebuilds the index
        without the deleted documents.
        """
        if not ids:
            return

        try:
            # Find indices to keep
            keep_indices = []
            keep_docs = []
            
            for i, doc in enumerate(self.documents):
                if doc.id not in ids:
                    keep_indices.append(i)
                    keep_docs.append(doc)

            if len(keep_docs) == len(self.documents):
                logger.info("No documents to delete")
                return

            # Rebuild index with remaining documents
            if keep_docs and keep_docs[0].embedding:
                embeddings = [doc.embedding for doc in keep_docs if doc.embedding]
                if embeddings:
                    embeddings_array = np.array(embeddings).astype('float32')
                    
                    # Create new index
                    self.index = faiss.IndexFlatIP(self.dimension)
                    normalized_vectors = self._normalize_vectors(embeddings_array)
                    self.index.add(normalized_vectors)
                    
                    self.documents = keep_docs
                    
                    # Save updated index
                    self._save()
                    
                    logger.success("Deleted {} documents", len(ids))
                else:
                    logger.warning("Cannot rebuild index: missing embeddings")
            else:
                # If no documents left, clear everything
                self.index = None
                self.documents = []
                self._save()
                
                logger.info("Cleared all documents")

        except Exception:
            logger.exception("Failed to delete documents")
            raise

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        try:
            # Remove files
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)
            
            # Reset in-memory state
            self.index = None
            self.documents = []
            self.dimension = None
            
            logger.info("Deleted collection {}", self.collection_name)
            
        except Exception as e:
            logger.error("Failed to delete collection: {}", e)
            raise

    def get_document_count(self) -> int:
        """Get number of documents in the store."""
        return len(self.documents)

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        return {
            "name": self.collection_name,
            "document_count": self.get_document_count(),
            "dimension": self.dimension,
            "persist_directory": self.persist_directory,
            "index_type": type(self.index).__name__ if self.index else None,
        }