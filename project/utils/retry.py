import asyncio
import logging
import time
from functools import wraps
from typing import Callable, Iterable

logger = logging.getLogger(__name__)


def retry_on_exception(
    exceptions: type[Exception] | Iterable[type[Exception]],
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 1.0,
    on_retry: Callable[[int, Exception], None] | None = None,
):
    """
    Декоратор для автоматического повторного выполнения функции при возникновении указанных исключений.

    Args:
        exceptions: Исключение или кортеж исключений, при которых нужно повторять попытку
        max_attempts: Максимальное количество попыток (включая первую)
        delay: Начальная задержка между попытками в секундах
        backoff: Множитель для увеличения задержки после каждой неудачной попытки
        on_retry: Функция обратного вызова, вызываемая при каждой повторной попытке
    """
    if isinstance(exceptions, type):
        exceptions = (exceptions,)

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                current_delay = delay
                for attempt in range(1, max_attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_attempts:
                            logger.error(
                                "Failed after %s attempts (func=%s): %s: %s",
                                max_attempts,
                                func.__name__,
                                e.__class__.__name__,
                                e,
                            )
                            raise

                        logger.warning(
                            "Retry %s/%s (func=%s) on %s: %s; sleep=%.2fs",
                            attempt,
                            max_attempts,
                            func.__name__,
                            e.__class__.__name__,
                            e,
                            current_delay,
                        )
                        if on_retry is not None:
                            on_retry(attempt, e)

                        await asyncio.sleep(current_delay)
                        current_delay *= backoff

                return None

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            "Failed after %s attempts (func=%s): %s: %s",
                            max_attempts,
                            func.__name__,
                            e.__class__.__name__,
                            e,
                        )
                        raise

                    logger.warning(
                        "Retry %s/%s (func=%s) on %s: %s; sleep=%.2fs",
                        attempt,
                        max_attempts,
                        func.__name__,
                        e.__class__.__name__,
                        e,
                        current_delay,
                    )
                    if on_retry is not None:
                        on_retry(attempt, e)

                    time.sleep(current_delay)
                    current_delay *= backoff

            return None

        return sync_wrapper

    return decorator


def retry_unless_exception(
    excluded_exceptions: type[Exception] | Iterable[type[Exception]],
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 1.0,
    on_retry: Callable[[int, Exception], None] | None = None,
):
    """
    Декоратор, который НЕ делает повторов для выбранных исключений, а для остальных
    предпринимает повторы по тем же правилам, что и retry_on_exception.

    Args:
        excluded_exceptions: Исключение или набор исключений, для которых повторы
            делаться не должны (будет мгновенный проброс исключения без ретраев).
        max_attempts: Максимальное количество попыток (включая первую) для остальных исключений.
        delay: Начальная задержка между попытками в секундах.
        backoff: Множитель для увеличения задержки после каждой неудачной попытки.
        on_retry: Функция обратного вызова, вызываемая перед каждой повторной попыткой.
    """
    if not isinstance(excluded_exceptions, Iterable):
        excluded_exceptions = (excluded_exceptions,)

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                current_delay = delay
                for attempt in range(1, max_attempts + 1):
                    try:
                        return await func(*args, **kwargs)

                    except excluded_exceptions:
                        # Для указанных исключений не делаем повторов
                        raise

                    except Exception as e:  # pylint: disable=broad-except
                        if attempt == max_attempts:
                            logger.error(
                                "Failed after %s attempts (func=%s): %s: %s",
                                max_attempts,
                                func.__name__,
                                e.__class__.__name__,
                                e,
                            )
                            raise

                        logger.warning(
                            "Retry %s/%s (func=%s) on %s: %s; sleep=%.2fs",
                            attempt,
                            max_attempts,
                            func.__name__,
                            e.__class__.__name__,
                            e,
                            current_delay,
                        )
                        if on_retry is not None:
                            on_retry(attempt, e)

                        await asyncio.sleep(current_delay)

                        current_delay *= backoff

                return None

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except excluded_exceptions:
                    # Для указанных исключений не делаем повторов
                    raise

                except Exception as e:  # pylint: disable=broad-except
                    if attempt == max_attempts:
                        raise

                    logger.warning(
                        "Retry %s/%s (func=%s) on %s: %s; sleep=%.2fs",
                        attempt,
                        max_attempts,
                        func.__name__,
                        e.__class__.__name__,
                        e,
                        current_delay,
                    )
                    if on_retry is not None:
                        on_retry(attempt, e)

                    time.sleep(current_delay)
                    current_delay *= backoff

            return None

        return sync_wrapper

    return decorator
