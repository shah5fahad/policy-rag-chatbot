# src/ai/agent_manager.py

import asyncio
import random
from typing import Any, Optional, Callable, Awaitable

from loguru import logger
from pydantic_ai.exceptions import ModelHTTPError

from .model_factory import ModelFactory
from .config import AIModelProvider


class AgentManager:
    """
    Enterprise Agent Orchestration Layer

    Features:
    - Exponential backoff with jitter
    - Timeout protection
    - Retry classification
    - Structured logging
    - Cancellation safety
    """

    DEFAULT_RETRIES = 3
    MAX_BACKOFF = 60.0
    BASE_DELAY = 1.0
    DEFAULT_TIMEOUT = 120.0

    @classmethod
    async def run_with_backoff(
        cls,
        agent,
        *args,
        retries: int = DEFAULT_RETRIES,
        base_delay: float = BASE_DELAY,
        timeout: float = DEFAULT_TIMEOUT,
        correlation_id: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Executes agent.run() with:
        - Timeout protection
        - Exponential backoff
        - Jitter
        - Intelligent retry logic
        """

        delay = base_delay

        for attempt in range(1, retries + 1):
            try:
                logger.bind(
                    correlation_id=correlation_id
                ).debug(
                    "LLM attempt {}/{}", attempt, retries
                )

                return await asyncio.wait_for(
                    agent.run(*args, **kwargs),
                    timeout=timeout,
                )

            except asyncio.TimeoutError:
                logger.bind(
                    correlation_id=correlation_id
                ).warning("LLM request timed out")

            except ModelHTTPError as exc:
                logger.bind(
                    correlation_id=correlation_id
                ).warning(
                    "HTTP/Rate limit error: {}", str(exc)
                )

            except asyncio.CancelledError:
                logger.warning("LLM task was cancelled")
                raise

            except Exception as exc:
                logger.bind(
                    correlation_id=correlation_id
                ).exception(
                    "Unexpected error during LLM execution: {}",
                    str(exc),
                )

            sleep_time = cls._calculate_backoff(
                attempt=attempt,
                base_delay=delay,
            )

            logger.bind(
                correlation_id=correlation_id
            ).debug(
                "Retrying in {:.2f}s (attempt {}/{})",
                sleep_time,
                attempt,
                retries,
            )

            await asyncio.sleep(sleep_time)

        raise RuntimeError(
            "Exceeded maximum retries for LLM request"
        )

    @classmethod
    def _calculate_backoff(
        cls,
        attempt: int,
        base_delay: float,
    ) -> float:
        """
        Exponential backoff with full jitter.
        """

        exponential = base_delay * (2 ** (attempt - 1))
        capped = min(exponential, cls.MAX_BACKOFF)

        # Full jitter strategy (AWS recommended)
        return random.uniform(0, capped)

    @staticmethod
    def create_agent(
        system_prompt: str,
        output_type: Any,
        provider: Optional[AIModelProvider] = None,
        is_embedding: bool = False,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ):
        """
        Factory wrapper to centralize agent creation.
        Keeps imports clean across codebase.
        """

        logger.debug(
            "Creating agent | provider={} temperature={} max_tokens={}",
            provider,
            temperature,
            max_tokens,
        )

        return ModelFactory.create_agent(
            system_prompt=system_prompt,
            output_type=output_type,
            provider=provider,
            is_embedding=is_embedding,
            temperature=temperature,
            max_tokens=max_tokens,
        )