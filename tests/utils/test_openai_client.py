import pytest
import json
from src.utils import OpenAIClient

@pytest.mark.asyncio
class TestOpenAIClient:
    @pytest.mark.asyncio
    async def test_aenter_success(self):
        async with OpenAIClient(instruction_no=0) as client:
            assert isinstance(client, OpenAIClient)

    @pytest.mark.asyncio
    async def test_create_chat_completions_streamed_response(self):
        async with OpenAIClient(instruction_no=0) as client:
            chunks = [chunk async for chunk in client.create_chat_completions([{'role': 'user', 'content': 'test'}])]
            chunks = "".join(chunks)
            chunks = json.loads(chunks)
            assert "form_1099_div_data" in chunks
        async with OpenAIClient(instruction_no=1) as client:
            chunks = [chunk async for chunk in client.create_chat_completions([{'role': 'user', 'content': 'test'}])]
            chunks = "".join(chunks)
            chunks = json.loads(chunks)
            assert "form_w2_data" in chunks
        async with OpenAIClient(instruction_no=2) as client:
            chunks = [chunk async for chunk in client.create_chat_completions([{'role': 'user', 'content': 'test'}])]
            chunks = "".join(chunks)
            chunks = json.loads(chunks)
            assert "form_1099_int_data" in chunks
