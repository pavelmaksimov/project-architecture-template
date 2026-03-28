# Обработка дисконнектов клиентов в FastAPI

При работе с LLM и стриминговыми ответами важно корректно обрабатывать ситуации,
когда клиент неожиданно закрывает соединение. Без обработки дисконнектов:
- GPU продолжает генерацию токенов впустую
- Транзакции в БД могут остаться незавершёнными
- Ресурсы сервера тратятся впустую

## Расположение

`project/infrastructure/utils/disconnect.py`

## Основные концепции

### Как работает обнаружение дисконнекта

ASGI-сервер (Uvicorn) отправляет событие `http.disconnect` при закрытии соединения.
Для обнаружения нужно явно опрашивать `await request.receive()` и проверять тип сообщения.

**Важно:** Не используйте `request.is_disconnected()` — он некорректно работает с `BaseHTTPMiddleware`.

## Автоматическая обработка через Middleware (рекомендуется)

Добавьте `DisconnectMiddleware` в приложение — он автоматически обрабатывает дисконнекты для обычных эндпоинтов.

```python
from fastapi import FastAPI
from project.infrastructure.utils.disconnect import DisconnectMiddleware

app = FastAPI()
app.add_middleware(DisconnectMiddleware)
```

**Примечание:** Для стриминговых эндпоинтов (StreamingResponse, EventSourceResponse) middleware пропускает обработку, так как они имеют встроенную логику отмены. Для стриминга используйте `detect_disconnect()` или полагайтесь на `sse-starlette`.

## Утилиты для ручной обработки

### 1. Декоратор `@with_cancellation`

Для обычных (не-стриминговых) эндпоинтов — автоматически отменяет обработчик при дисконнекте.

```python
from project.infrastructure.utils.disconnect import with_cancellation
from fastapi import Request

@app.post("/process")
@with_cancellation
async def process_job(job: JobRequest, raw_request: Request):
    try:
        result = await llm.generate(job.prompt)
        return {"result": result}
    except asyncio.CancelledError:
        # Логируем отмену, отправляем метрики
        raise  # Пробрасываем исключение дальше
    finally:
        # Очистка ресурсов с защитой от отмены
        with shield_cancel_scope():
            await cleanup()
```

### 2. Контекстный менеджер `detect_disconnect`

Для гранулярного контроля — защищает критичные операции и позволяет отменять выборочно.

```python
from project.infrastructure.utils.disconnect import detect_disconnect, cancel_on_disconnect

@app.post("/process")
async def process_job(job: JobRequest, request: Request):
    async with detect_disconnect(request) as disconnect_event:
        # Защищено от отмены — выполнится всегда
        await db.log_request(job.job_id)

        # Проверяем, отключился ли клиент
        if disconnect_event.is_set():
            await db.log_cancellation(job.job_id)
            return Response(status_code=499)

        # Может быть отменено при дисконнекте
        result = await cancel_on_disconnect(
            expensive_operation(),
            disconnect_event
        )

        return result
```

### 3. Функция `shield_cancel_scope`

Защита критичных операций от отмены в стриминговых ответах.

```python
from project.infrastructure.utils.disconnect import shield_cancel_scope

async def stream_response():
    try:
        async with aclosing(generate_chunks()) as gen:
            async for chunk in gen:
                yield chunk
    finally:
        with shield_cancel_scope():
            await cleanup()  # Не будет прервано при отмене
```

### 4. Функция `safe_async_generator_cleanup`

Безопасная очистка асинхронных генераторов через `aclosing()`.

```python
from project.infrastructure.utils.disconnect import safe_async_generator_cleanup
from contextlib import aclosing

async def generate_llm_response():
    async with aclosing(llm_stream()) as stream:
        async for chunk in stream:
            yield chunk
        # aclosing() гарантирует немедленное освобождение ресурсов
```

## Особенности реализации

### Использование anyio.CancelScope для стриминга

При работе с `sse-starlette` и стриминговыми ответами используйте `anyio.CancelScope`
вместо `asyncio.shield()`, так как sse-starlette работает на anyio task groups.

```python
import anyio

with anyio.CancelScope(shield=True):
    await cleanup_operation()
```

### Обработка CancelledError

Всегда явно обрабатывайте `CancelledError`:
- Логируйте событие отмены
- Отправляйте метрики
- Пробрасывайте исключение дальше
- Выполняйте очистку в `finally` блоке

```python
try:
    result = await operation()
except asyncio.CancelledError:
    # Логируем метрику отмены
    metrics.increment("request_cancelled")
    raise  # Пробрасываем
```

### Избегайте двойной отмены

Не проверяйте дисконнект вручную внутри стриминговых генераторов, если уже
используете `EventSourceResponse` или `StreamingResponse` — фреймворки
уже обрабатывают отмену. Ручная проверка создаёт race condition.

## Когда что использовать

| Сценарий | Инструмент |
|----------|------------|
| Все эндпоинты автоматически | `DisconnectMiddleware` |
| Простой endpoint без стриминга (без middleware) | `@with_cancellation` |
| Нужна защита БД-операций | `detect_disconnect` |
| Стриминговый ответ (SSE) | `shield_cancel_scope` + `aclosing()` |
| Сложная логика с несколькими этапами | Комбинация инструментов |

## Ссылки

- [Статья на Habr](https://habr.com/ru/companies/tochka/articles/992134/)
- [vLLM implementation](https://github.com/vllm-project/vllm/blob/v0.13.0/vllm/entrypoints/utils.py)
