import os

from dotenv import load_dotenv

from .app import app

if os.getenv("PYTHON_ENV") == "test":
    load_dotenv(dotenv_path=".env.test", override=True)
else:
    load_dotenv()

if not os.getenv("SQLALCHEMY_DATABASE_URI"):
    raise ValueError("SQLALCHEMY_DATABASE_URI environment not set.")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment not set.")

if not os.getenv("SCHEDULER_INTERVAL"):
    raise ValueError("SCHEDULER_INTERVAL environment not set.")

if not os.getenv("PINECONE_API_KEY"):
    raise ValueError("PINECONE_API_KEY environment not set.")

if not os.getenv("PINECONE_INDEX_NAME"):
    raise ValueError("PINECONE_INDEX_NAME environment not set.")

__all__ = ["app"]
__version__ = "0.1.0"
__author__ = "Kanha Upadhyay"
