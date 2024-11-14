import os

from openai import AsyncOpenAI


class OpenAIClient:
    def __init__(
        self, model: str = "gpt-4o-2024-08-06", timeout: int = 300, max_retries: int = 5
    ):
        self._client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=timeout,
            max_retries=max_retries,
        )
        self._model = model

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._client.close()

    async def parse_data(self, instruction: str, response_format: type, content: str):
        completion = await self._client.beta.chat.completions.parse(
            model=self._model,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": content},
            ],
            response_format=response_format,
        )
        return completion.choices[0].message.parsed
