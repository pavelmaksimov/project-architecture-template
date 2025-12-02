from functools import cache

import cohere
import langchain_openai
import openai
from llm_common.clients.llm_http_client import LLMHttpClient

from project.settings import Settings


@cache
def llm_chat_client(
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    streaming: bool = False,
    timeout: float | None = None,
) -> langchain_openai.ChatOpenAI:
    """Client with prometheus monitoring."""
    return langchain_openai.ChatOpenAI(
        api_key=Settings().LLM_API_KEY.get_secret_value(),
        base_url=Settings().LLM_MIDDLE_PROXY_URL if Settings().is_any_stand() else None,
        model=model or Settings().LLM_MODEL,
        temperature=Settings().LLM_TEMPERATURE if temperature is None else temperature,
        max_tokens=max_tokens or Settings().LLM_MAX_TOKENS,
        http_async_client=LLMHttpClient(),
        streaming=streaming,
        timeout=timeout or Settings().LLM_TIMEOUT,
    )


@cache
def llm_client(timeout: float | None = None) -> openai.AsyncClient:
    """
    Client with prometheus monitoring.

    Example completions usage:
        response = await llm_aclient().chat.completions.create(
            model=Settings().LLM_MODEL,
            messages=[],
            temperature=0.7,
            top_p=0.8,
            max_tokens=8192,
        )
        answer = response.choices[0].message.content
        print(answer)

    Example embeddings usage:
        response = await llm_aclient().embeddings.create(
            model=Settings().LLM_EMBEDDINGS_MODEL,
            input=["Мой", "вопрос"]
        )
        result = response.data
        print(result)
    """
    return openai.AsyncClient(
        api_key=Settings().LLM_API_KEY.get_secret_value(),
        base_url=Settings().LLM_MIDDLE_PROXY_URL if Settings().is_any_stand() else None,
        http_client=LLMHttpClient(),
        timeout=timeout or Settings().LLM_TIMEOUT,
    )


@cache
def reranker_client(timeout: float | None = None) -> cohere.AsyncClient:
    """
    Client with prometheus monitoring.

    Example usage:
        await reranker_client().rerank(
            model=Settings().LLM_RERANK_MODEL,
            query="...",
            documents=[...],
            top_n=3,
        )

    """
    return cohere.AsyncClient(
        api_key=Settings().LLM_API_KEY.get_secret_value(),
        base_url=Settings().LLM_MIDDLE_PROXY_URL if Settings().is_any_stand() else None,
        httpx_client=LLMHttpClient(),
        timeout=timeout or Settings().LLM_TIMEOUT,
    )
