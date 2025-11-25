import asyncio
import logging
from functools import wraps
from typing import Callable, Any

from telegram import Update
from telegram.ext import ContextTypes

from project.exceptions import AuthError
from project.infrastructure.adapters.auth import auth_client
from project.libs.log import get_log_id
from project.settings import Settings

logger = logging.getLogger(__name__)

failed_message = "Произошла ошибка. Код ошибки {log_id}"
processing_retry_message = "⏳ Превышено время ожидания. Повторная попытка..."
processing_message_with_retry = "⏳ Обработка... (макс. ожидание {timeout} сек.)"


def processing_errors(func):
    """
    Чтоб в каждом обработчике не дублировать код по обработке ошибок,
    используйте этот декоратор, как централизованне место для перехвата и обработки ошибок в хендлерах.
    Внутри хендлеров не нужно подавлять ошибки.
    """

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            return await func(update, context)

        except AuthError as exc:
            logger.info("User %s is not authenticated", update.effective_user.id)
            await update.effective_message.reply_text(text=str(exc))

        except Exception:
            log_id = get_log_id(update.effective_user.id)
            logger.exception("Error start_handler %s", log_id)
            await update.message.reply_text(failed_message.format(log_id=log_id))

    return wrapper


def check_auth(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if Settings().is_local():
            return await func(update, context)

        user_id = update.effective_user.id
        if not await auth_client().check_telegram_user(user_id):  # di: skip
            raise AuthError(user_id)

        return await func(update, context)

    return wrapper


def timeout_with_retry(
    timeout: float = 180,
    max_attempts: int = 3,
    *,
    retry_message: str | None = processing_retry_message,
    failed_message: str | None = failed_message,
    processing_message_on: bool = False,
):
    """
    Декоратор для обработчиков Telegram с таймаутом и повторными попытками.
    При превышении таймаута отправляет сообщение пользователю с предупреждением,
    что превышено макс. время ожидание и будет сделана повторная попытка.

    Args:
        timeout: Максимальное время выполнения в секундах
        max_attempts: Максимальное количество попыток
        processing_message: Временное сообщение для отправки перед обработкой
        retry_message: Сообщение для отправки пользователю при повторной попытке
        failed_message: Сообщение для отправки пользователю после всех неудачных попыток
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Извлекаем Update из аргументов.
            for arg in args:
                if isinstance(arg, Update):
                    update: Update = arg
                    break
            else:
                error = "Update not found in args"
                raise ValueError(error)

            processing_msg = None
            if processing_message_on:
                processing_msg = await update.effective_message.reply_text(
                    processing_message_with_retry.format(timeout=timeout),
                )
                await update.effective_message.chat.send_chat_action("typing")

            for attempt in range(max_attempts):  # noqa: RET503
                try:
                    # Выполняем функцию с таймаутом.
                    return await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout,
                    )

                except TimeoutError:
                    if attempt == max_attempts - 1:
                        # Все попытки исчерпаны - отправляем failure сообщение.
                        if failed_message:
                            await update.effective_message.reply_text(
                                failed_message.format(log_id=get_log_id(update.effective_chat.id)),
                            )

                        raise

                    logger.warning(
                        "Timeout Error in %s (attempt %s/%s)",
                        func.__name__,
                        attempt,
                        max_attempts,
                    )

                    # Если не последняя попытка, отправляем retry сообщение.
                    if retry_message:
                        await update.effective_message.reply_text(retry_message)

                finally:
                    if processing_msg:
                        await processing_msg.delete()
                        processing_msg = None

        return wrapper

    return decorator
