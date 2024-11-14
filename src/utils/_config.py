import os

from dotenv import load_dotenv
from loguru import logger

if os.getenv("PYTHON_ENV") == "test":
    load_dotenv(dotenv_path=".env.test", override=True)
else:
    load_dotenv()


LOG_FILE = os.getenv("LOG_FILE")
if LOG_FILE:
    LOG_RETENTION = os.getenv("LOG_RETENTION", "90 days")
    logger.add(LOG_FILE, retention=LOG_RETENTION)

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
