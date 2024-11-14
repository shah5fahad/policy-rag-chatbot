import os

from loguru import logger

LOG_FILE = os.getenv("LOG_FILE")
if LOG_FILE:
    LOG_RETENTION = os.getenv("LOG_RETENTION", "90 days")
    logger.add(LOG_FILE, retention=LOG_RETENTION)
