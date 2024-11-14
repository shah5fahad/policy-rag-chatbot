import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone


class PineconeClient:
    def __init__(self):
        self.pc = Pinecone(
            api_key=os.getenv("PINECONE_API_KEY"),
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

    async def __aenter__(self):
        self.index = self.pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        self.vector_store = PineconeVectorStore(
            index=self.index, embedding=self.embeddings
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def insert_data(self, text: list[str], metadata: list[dict]):
        return await self.vector_store.aadd_texts(texts=text, metadatas=metadata)

    async def similarity_search(self, query: str, top_k: int = 5):
        return await self.vector_store.asimilarity_search_with_score(
            query=query, k=top_k
        )

    async def delete(self, ids: list[str]):
        return await self.vector_store.adelete(ids=ids)

    async def similarity_search_by_vector(
        self, query_vector: list[float], top_k: int = 5
    ):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool,
                lambda: self.index.query(
                    vector=query_vector, top_k=top_k, include_metadata=True
                ),
            )
