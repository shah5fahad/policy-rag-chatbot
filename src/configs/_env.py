import os

from dotenv import load_dotenv

load_dotenv()


class EnvConfig:
    DATABASE_URI: str = os.getenv("DATABASE_URI")
    CORS_ALLOW_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ALLOW_ORIGINS", "localhost, 127.0.0.1").split(",")
        if origin.strip()
    ]
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME")

    @classmethod
    def validate_required_vars(cls):
        required_vars = [
            "DATABASE_URI",
            "OPENAI_API_KEY",
            "PINECONE_API_KEY",
            "PINECONE_INDEX_NAME",
        ]
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        if missing_vars:
            raise ValueError(
                f"Missing environment variables: {', '.join(missing_vars)}"
            )


EnvConfig.validate_required_vars()
