from functools import cache

import cohere
from langchain_openai import ChatOpenAI
from llm_common.clients.llm_http_client import LLMHttpClient
from openai import AsyncClient

from project.settings import Settings


@cache
def llm_chat_client():
    """Client with prometheus monitoring."""
    return ChatOpenAI(
        api_key=Settings().LLM_API_KEY.get_secret_value(),
        base_url=Settings().LLM_MIDDLE_PROXY_URL if Settings().is_any_stand() else None,
        model=Settings().LLM_MODEL,
        temperature=Settings().LLM_TEMPERATURE,
        max_tokens=Settings().LLM_MAX_TOKENS,
        streaming=False,
        http_async_client=LLMHttpClient(),
    )


@cache
def llm_aclient() -> AsyncClient:
    """Client with prometheus monitoring."""
    return AsyncClient(
        api_key=Settings().LLM_API_KEY.get_secret_value(),
        base_url=Settings().LLM_MIDDLE_PROXY_URL if Settings().is_any_stand() else None,
        http_client=LLMHttpClient(),
    )


@cache
def reranker_client() -> cohere.AsyncClient:
    """
    Client with prometheus monitoring.

    Example usage:
        await reranker_client().rerank(
            model=Settings().RERANK_MODEL,
            query="...",
            documents=[...],
            top_n=3,
        )

    """
    return cohere.AsyncClient(
        api_key=Settings().LLM_API_KEY.get_secret_value(),
        base_url=Settings().LLM_MIDDLE_PROXY_URL if Settings().is_any_stand() else None,
        httpx_client=LLMHttpClient(),
    )
