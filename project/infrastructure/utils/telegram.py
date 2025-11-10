import logging
from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from project.exceptions import AuthError
from project.infrastructure.adapters.auth import auth_client
from project.libs.log import get_log_id

logger = logging.getLogger(__name__)


def processing_errors(func):
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
            await update.message.reply_text("Произошла ошибка. Код ошибки для отладки %s", log_id)

    return wrapper


def check_auth(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not await auth_client().check_telegram_user(user_id):  # di: skip
            raise AuthError(user_id)

        return await func(update, context)

    return wrapper
