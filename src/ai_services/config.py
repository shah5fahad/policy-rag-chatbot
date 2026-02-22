import os
from enum import Enum
from typing import Optional, Dict


class AIModelProvider(str, Enum):
    """
    Enum for supported AI model providers.
    Using str inheritance ensures compatibility with configs and serialization.
    """
    OPENAI = "openai"
    GEMINI = "google-gla"
    HUGGINGFACE = "huggingface"
    
    
class AIModelType(str, Enum):
    """
    Enum for model types.
    """
    EMBEDDING = 0
    LLM = 1


class AISettings:
    """
    Centralized AI configuration settings.
    Values can be overridden via environment variables.
    """
    # Path to vector store (e.g., Chroma, FAISS)
    VECTOR_STORE_PATH: str = os.getenv("CHROMA_PATH", "database/faiss_vector_db")
    # Selected provider (openai | gemini | huggingface)
    PROVIDER: AIModelProvider = AIModelProvider(os.getenv("AI_PROVIDER", "google-gla"))
    
    # Mapping of provider → model types (embedding & LLM)
    PROVIDER_MODEL_MAPPING: Dict[AIModelProvider, Dict[str, Optional[str]]] = {
        AIModelProvider.OPENAI: {
            AIModelType.EMBEDDING : os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            AIModelType.LLM: os.getenv("OPENAI_MODEL", "gpt-5.2"),
        },
        AIModelProvider.GEMINI: {
            AIModelType.EMBEDDING : os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"),
            AIModelType.LLM: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        },
        AIModelProvider.HUGGINGFACE: {
            AIModelType.EMBEDDING : os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            AIModelType.LLM: None,  # Typically HF models are used for embeddings only
        },
    }

    @classmethod
    def get_embedding_model_name(cls, provider: AIModelProvider) -> str:
        """
        Returns the embedding model for the selected provider.
        """
        return cls.PROVIDER_MODEL_MAPPING[provider][AIModelType.EMBEDDING]

    @classmethod
    def get_llm_model_name(cls, provider: AIModelProvider) -> str:
        """
        Returns the LLM model for the selected provider, or None if unavailable.
        """
        return cls.PROVIDER_MODEL_MAPPING[provider][AIModelType.LLM]