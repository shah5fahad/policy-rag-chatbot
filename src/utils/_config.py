import os

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


LOG_FILE = os.getenv("LOG_FILE")
if LOG_FILE:
    logger.add(LOG_FILE, retention="10 days")

if not os.getenv("SQLALCHEMY_DATABASE_URI"):
    logger.error("SQLALCHEMY_DATABASE_URI environment not set.")
    raise ValueError("SQLALCHEMY_DATABASE_URI environment not set.")

if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY environment not set.")
    raise ValueError("OPENAI_API_KEY environment not set.")

if not os.getenv("SCHEDULER_INTERVAL"):
    logger.error("SCHEDULER_INTERVAL environment not set.")
    raise ValueError("SCHEDULER_INTERVAL environment not set.")

if not os.getenv("PINECONE_API_KEY"):
    logger.error("PINECONE_API_KEY environment not set.")
    raise ValueError("PINECONE_API_KEY environment not set.")

if not os.getenv("PINECONE_INDEX_NAME"):
    logger.error("PINECONE_INDEX_NAME environment not set.")
    raise ValueError("PINECONE_INDEX_NAME environment not set.")
