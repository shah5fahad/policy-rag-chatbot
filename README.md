# Policy Reader Chatbot  
## RAG-Based Document Q&A System

## Overview

Policy Reader Chatbot is a Retrieval-Augmented Generation (RAG) based document question-answering system.

It allows users to:

- Upload documents (PDF, DOCX, TXT)
- Process and index document content
- Ask natural language questions
- Receive accurate answers generated using Google Gemini AI

The system combines document retrieval with AI-powered answer generation to ensure responses are based strictly on uploaded document content.

---

## How the System Works

1. A user uploads a document.
2. The system extracts text from the document.
3. The text is split into smaller chunks.
4. Each chunk is converted into vector embeddings.
5. The embeddings are stored in a FAISS vector database.
6. When a user asks a question:
   - The system converts the question into an embedding.
   - It finds the most relevant document chunks.
   - Those chunks are sent to Gemini AI.
   - Gemini generates an answer using only the retrieved context.

This approach ensures answers are accurate and grounded in the document.

---

## Technology Used

- FastAPI — Backend REST API
- Streamlit — Frontend user interface
- SQLAlchemy — Database ORM
- SQLite (local) / PostgreSQL (production)
- FAISS — Vector similarity search
- Sentence Transformers — Text embeddings
- Google Gemini AI — Answer generation
- PyPDF2 & python-docx — Document parsing

---

## How to Set Up Locally

### Prerequisites

- Python 3.10 to 3.12
- Google Gemini API Key (Get it from https://makersuite.google.com/app/apikey)
- Git installed

---

# Local Setup Guide (Poetry)

This guide explains how to set up and run the project locally using
**Poetry**.

------------------------------------------------------------------------

## Prerequisites

-   Python 3.10 -- 3.12
-   Poetry installed
-   Git installed

------------------------------------------------------------------------

## Install Poetry (If Not Installed)

### Windows (PowerShell)

``` bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### macOS / Linux

``` bash
curl -sSL https://install.python-poetry.org | python3 -
```

Verify installation:

``` bash
poetry --version
```

------------------------------------------------------------------------

## Clone the Repository

``` bash
git clone https://github.com/shah5fahad/policy-rag-chatbot
```

------------------------------------------------------------------------

## Install Dependencies

``` bash
poetry install
```

This will create a virtual environment and install all required
dependencies from `pyproject.toml`.

------------------------------------------------------------------------

## Activate Virtual Environment

``` bash
poetry shell
```

Alternatively, you can run commands without activating:

``` bash
poetry run <command>
```

------------------------------------------------------------------------

## Run Database Migrations

``` bash
poetry run alembic upgrade head
```

------------------------------------------------------------------------

## Start Backend Server

``` bash
poetry run python main.py
```

Backend URL:

    http://localhost:8000

API Docs:

    http://localhost:8000/docs

------------------------------------------------------------------------

## Start Frontend (Streamlit)

Open a new terminal in the project root:

``` bash
cd streamlit_app
poetry run streamlit run app.py
```

Frontend URL:

    http://localhost:8501

------------------------------------------------------------------------

## Common Useful Commands

Update dependencies:

``` bash
poetry update
```

Add new dependency:

``` bash
poetry add package_name
```

Deactivate virtual environment:

``` bash
exit
```