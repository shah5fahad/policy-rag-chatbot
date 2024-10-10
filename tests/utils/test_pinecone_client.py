import os
import pytest
from unittest.mock import patch, AsyncMock, ANY
from src.utils import PineconeClient

@pytest.mark.asyncio
class TestPineconeClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.index_name = "test"
        self.text_data = ["sample text 1", "sample text 2"]
        self.metadata = [{"id": "1"}, {"id": "2"}]
        self.query_vector = [0.1]*1536
        self.query = "sample query"
        self.top_k = 3
        os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

    async def test_insert_data(self):
        with patch("langchain_pinecone.PineconeVectorStore.aadd_texts", new_callable=AsyncMock) as mock_aadd_texts:
            mock_aadd_texts.return_value = ["id1", "id2"]
            async with PineconeClient() as pinecone_client:
                result = await pinecone_client.insert_data(self.text_data, self.metadata)
            mock_aadd_texts.assert_awaited_once_with(
                texts=self.text_data, metadatas=self.metadata
            )
            assert result == ["id1", "id2"]

    async def test_similarity_search(self):
        with patch("langchain_pinecone.PineconeVectorStore.asimilarity_search_with_score", new_callable=AsyncMock) as mock_asimilarity_search:
            mock_results = [("sample result", 0.9)]
            mock_asimilarity_search.return_value = mock_results
            async with PineconeClient() as pinecone_client:
                result = await pinecone_client.similarity_search(self.query, self.top_k)
            mock_asimilarity_search.assert_awaited_once_with(query=self.query, k=self.top_k)
            assert result == mock_results

    async def test_delete(self):
        with patch("langchain_pinecone.PineconeVectorStore.adelete", new_callable=AsyncMock) as mock_adelete:
            ids_to_delete = ["id1", "id2"]
            mock_adelete.return_value = True
            async with PineconeClient() as pinecone_client:
                result = await pinecone_client.delete(ids_to_delete)
            mock_adelete.assert_awaited_once_with(ids=ids_to_delete)
            assert result is True

    async def test_similarity_search_by_vector(self):
        async with PineconeClient() as pinecone_client:
            result = await pinecone_client.similarity_search_by_vector(self.query_vector, self.top_k)
        assert result is not None
