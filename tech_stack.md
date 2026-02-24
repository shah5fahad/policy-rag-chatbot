# Tech Stack

This document outlines the technology stack used in this project.

## ML/DL Basics

-   **NumPy**: Used for numerical operations, particularly for handling embeddings.
    -   **File**: `src/ai_services/vector_store.py`
    -   **Usage**: Converting lists of embeddings to NumPy arrays for efficient processing with FAISS.

## Generative AI & LLMs

-   **pydantic.ai**: The primary framework for interacting with Large Language Models (LLMs).
    -   **Files**:
        -   `src/ai_services/agent_manager.py`: Manages LLM requests and exceptions.
        -   `src/ai_services/embedding_factory.py`: Creates embeddings using `pydantic_ai`.
        -   `src/ai_services/model_factory.py`: Instantiates LLM agents.
    -   **Usage**: The project uses `pydantic-ai` to create and manage LLM agents, generate embeddings, and handle communication with LLM providers like OpenAI and Gemini.

-   **Transformers**: The project uses the `sentence-transformers` library for creating text embeddings.
    -   **File**: `src/ai_services/config.py`
    -   **Usage**: The `HF_EMBEDDING_MODEL` configuration specifies a `sentence-transformers` model to be used for generating embeddings.

## Vector Databases

The project supports multiple vector databases, with FAISS being the default.

-   **FAISS**: The default vector database for storing and searching document embeddings.
    -   **Files**:
        -   `src/ai_services/vector_store.py`: Contains the `FAISSVectorStore` class, which is a wrapper around the `faiss` library.
        -   `src/ai_services/rag_service.py`: Uses `FAISSVectorStore` for the RAG service.
    -   **Usage**: FAISS is used to index and search for similar documents based on their vector embeddings.

-   **Chroma**: An alternative vector database that can be used.
    -   **File**: `src/ai_services/chroma_store.py`: Contains the `ChromaVectorStore` class.
    -   **Usage**: The project can be configured to use Chroma instead of FAISS for vector storage and retrieval.

## Web Development

-   **FastAPI**: A modern web framework for building the backend API.
    -   **File**: `src/app.py`
    -   **Usage**: The main application is a FastAPI app that serves the backend API for the chatbot.

-   **Streamlit**: Used for creating the frontend user interface.
    -   **File**: `frontend/streamlit_app.py`
    -   **Usage**: The Streamlit app provides the chat interface for users to interact with the policy reader chatbot.
