import json
import os

from openai import AsyncOpenAI

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "file_search",
            "description": "Get the information from vector stores of files. Return docs and relevance scores in the range [0, 1] where 0 is dissimilar and 1 is most similar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for. You may use a file name, question, a sentence, or a paragraph. The search will return documents that are most similar to this query.",
                    }
                },
                "required": ["query"],
            },
        },
    }
]


AVAILABLE_FUNCTIONS = {
    "file_search": file_search,
}


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

    async def _handle_required_action(self, tool_calls: list[dict]):
        tool_calls_output = []
        for tool in tool_calls:
            if tool.type == "function":
                function_to_call = AVAILABLE_FUNCTIONS[tool.function.name]
                function_arguments = (
                    json.loads(tool.function.arguments)
                    if tool.function.arguments
                    else {}
                )
                function_response = await function_to_call(**function_arguments)
                tool_calls_output.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool.id,
                        "name": tool.function.name,
                        "content": (
                            str(function_response)
                            if function_response
                            else "No results found."
                        ),
                    }
                )
        return tool_calls_output

    async def _parse_response(self, delta, tool_call_response):
        if delta and delta.tool_calls:
            tool_call_chunk_list = delta.tool_calls
            for tool_call_chunk in tool_call_chunk_list:
                tool_call = tool_call_response.tool_calls[tool_call_chunk.index]
                if tool_call_chunk.function.arguments:
                    tool_call.function.arguments += tool_call_chunk.function.arguments
                    tool_call_response.tool_calls[tool_call_chunk.index] = tool_call
        return tool_call_response

    async def create_chat_completions(
        self,
        instructions: str,
        model: str = "gpt-4o",
        messages: list[str] = [],
        tools: list[dict] = TOOLS,
        tool_choice: str = "auto",
    ):
        messages_list = [
            {
                "role": "system",
                "content": f"{instructions}",
            }
        ]
        messages_list.extend(messages)
        response = await self._client.chat.completions.create(
            model=model,
            messages=messages_list,
            tools=tools,
            tool_choice=tool_choice,
            stream=True,
        )
        tool_call_response = None
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
            elif delta:
                if not tool_call_response:
                    tool_call_response = delta
                if not tool_call_response.tool_calls and delta.tool_calls:
                    tool_call_response.tool_calls = delta.tool_calls
                if (
                    tool_call_response
                    and delta.tool_calls
                    and len(tool_call_response.tool_calls)
                    < delta.tool_calls[0].index + 1
                ):
                    tool_call_response.tool_calls.append(delta.tool_calls[0])
                tool_call_response = await self._parse_response(
                    delta=delta, tool_call_response=tool_call_response
                )
        if tool_call_response and tool_call_response.tool_calls:
            tool_calls_output = await self._handle_required_action(
                tool_calls=tool_call_response.tool_calls
            )
            messages.append(tool_call_response)
            messages.extend(tool_calls_output)
            async for chunk in self.create_chat_completions(
                model=model, messages=messages, tools=tools, tool_choice=tool_choice
            ):
                yield chunk
