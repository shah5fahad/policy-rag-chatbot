# src/ai/model_factory.py

from typing import Optional
from pydantic_ai import Agent
from .config import AISettings, AIModelProvider


class ModelFactory:
    """
    Industrial-grade model factory.
    Handles LLM model instantiation across providers.
    """

    @classmethod
    def get_model_name(cls, provider: AIModelProvider = None, is_embedding: bool = False) -> str:
        if not provider:
            provider = AISettings.PROVIDER

        if provider not in AISettings.PROVIDER_MODEL_MAPPING:
            raise ValueError(f"Unsupported provider: {provider}")

        if is_embedding:
            return provider, AISettings.get_embedding_model_name(provider)
        else:
            return provider, AISettings.get_llm_model_name(provider)

    @classmethod
    def create_agent(
        cls,
        system_prompt: str,
        output_type,
        provider: Optional[AIModelProvider] = None,
        is_embedding: bool = False,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> Agent:
        """
        Creates a fully configured Agent instance.
        """
        provider, model_name = cls.get_model_name(provider=provider, is_embedding=is_embedding)

        return Agent(
            model=model_name,  # ← pass string directly
            system_prompt=system_prompt,
            output_type=output_type,
            retries=3,
            model_settings={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )