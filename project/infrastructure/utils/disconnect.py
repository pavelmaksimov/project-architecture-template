import asyncio
import functools
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import aclosing, asynccontextmanager, suppress
from typing import Any, Coroutine, TypeVar

import anyio
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

T = TypeVar("T")


async def listen_for_disconnect(request: Request) -> None:
    """Wait for http.disconnect event from the client."""
    while True:
        message = await request.receive()
        if message["type"] == "http.disconnect":
            break


def with_cancellation(handler_func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T | None]]:
    """
    Cancel endpoint handler when client disconnects.

    Usage:
        @app.post("/process")
        @with_cancellation
        async def process_job(job: JobRequest, raw_request: Request):
            ...
            raise asyncio.CancelledError()  # Re-raise after handling

    Note:
        Returns None on disconnect - response won't go anywhere.
    """

    @functools.wraps(handler_func)
    async def wrapper(*args: Any, **kwargs: Any) -> T | None:
        request = args[1] if len(args) > 1 else kwargs.get("raw_request")

        if request is None:
            return await handler_func(*args, **kwargs)

        handler_task = asyncio.create_task(handler_func(*args, **kwargs))
        cancellation_task = asyncio.create_task(listen_for_disconnect(request))

        done, pending = await asyncio.wait(
            [handler_task, cancellation_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

        if handler_task in done:
            return handler_task.result()
        return None

    return wrapper


async def _listen_for_http_disconnect(request: Request, event: asyncio.Event) -> None:
    """Wait for http.disconnect event and set the event."""
    while True:
        message = await request.receive()
        if message["type"] == "http.disconnect":
            event.set()
            break


@asynccontextmanager
async def detect_disconnect(request: Request) -> AsyncIterator[asyncio.Event]:
    """
    Async context manager providing event signaling client disconnection.

    Usage:
        @app.post("/process")
        async def process_job(job: JobRequest, request: Request):
            async with detect_disconnect(request) as disconnect_event:
                # Protected from cancellation - will always execute
                await db.log_request(job.job_id)

                # Can be cancelled on disconnect
                if disconnect_event.is_set():
                    await db.log_cancellation(job.job_id)
                    return Response(status_code=499)

                result = await expensive_operation()
                return result
    """
    disconnect_event = asyncio.Event()
    listener_task: asyncio.Task | None = None

    try:
        listener_task = asyncio.create_task(
            _listen_for_http_disconnect(request, disconnect_event),
        )
        yield disconnect_event
    finally:
        if listener_task is not None:
            with suppress(asyncio.CancelledError):
                listener_task.cancel()
                await listener_task


async def cancel_on_disconnect(
    work_coro: Coroutine[Any, Any, T],
    disconnect_event: asyncio.Event,
) -> T:
    """Return result of work_coro or raise CancelledError on disconnect."""
    work_task = asyncio.create_task(work_coro)
    disconnect_task = asyncio.create_task(disconnect_event.wait())

    done, pending = await asyncio.wait(
        [work_task, disconnect_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

    return work_task.result()


def shield_cancel_scope() -> anyio.CancelScope:
    """
    Return CancelScope with shield=True for protecting critical operations.

    Usage:
        async with shield_cancel_scope():
            await cleanup_operation()  # Will not be interrupted
    """
    return anyio.CancelScope(shield=True)


async def safe_async_generator_cleanup(
    generator: AsyncIterator[T],
) -> AsyncIterator[T]:
    """
    Safely cleanup async generator using aclosing().

    Ensures immediate resource release and proper context variable handling.

    Usage:
        async for chunk in generate_data():
            yield chunk
        # When cancelled, use:
        async with aclosing(generate_data()) as gen:
            async for chunk in gen:
                yield chunk
    """
    async with aclosing(generator) as gen:
        async for item in gen:
            yield item


class DisconnectMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically cancels non-streaming requests on client disconnect.

    Automatically monitors http.disconnect events and cancels the request handler.
    This saves resources when clients disconnect unexpectedly (e.g., closing browser tab
    during LLM processing).

    Note:
        Does NOT work with streaming responses (StreamingResponse, EventSourceResponse).
        For streaming endpoints, use detect_disconnect() context manager or rely on
        sse-starlette's built-in disconnect handling.

    Usage:
        app.add_middleware(DisconnectMiddleware)
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Запускаем две задачи параллельно:
        # 1. handler_task - выполнение эндпоинта
        # 2. disconnect_task - ожидание события http.disconnect от клиента
        handler_task = asyncio.create_task(call_next(request))
        disconnect_task = asyncio.create_task(listen_for_disconnect(request))

        # Ждём первую завершённую задачу из двух:
        # - Если эндпоинт выполнился быстрее - возвращаем результат
        # - Если клиент отключился первым - отменяем эндпоинт
        done, pending = await asyncio.wait(
            [handler_task, disconnect_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Эндпоинт завершился первым
        if handler_task in done:
            response = handler_task.result()
            # Проверяем: это стриминговый ответ?
            # У StreamingResponse/EventSourceResponse есть body_iterator.
            # Такие ответы имеют встроенную обработку дисконнекта через task group,
            # не нужно вмешиваться - просто возвращаем ответ как есть.
            if hasattr(response, "body_iterator"):
                return response

        # Отменяем незавершённую задачу и ждём её CancellationError
        # Если эндпоинт был быстрее - отменяем ожидание дисконнекта (disconnect_task)
        # Если дисконнект был первым - отменяем эндпоинт (handler_task)
        for task in pending:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

        # Возвращаем результат эндпоинта (обычный response)
        # Если эндпоинт уже вернул response - вернём его
        if handler_task in done:
            return handler_task.result()

        # Если эндпоинт был отменён из-за дисконнекта - вернём 499
        return Response(status_code=499)
