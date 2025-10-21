import datetime
import logging

from llm_common.prometheus import action_tracking
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)

logger = logging.getLogger(__name__)


def get_log_id(user_id):
    return f"{datetime.datetime.now().strftime("%y%m%d%H%M%S")}{user_id}"


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = "Привет! Это пример обработчика Телеграм!"

    try:
        with action_tracking("start_handler"):
            await update.message.reply_text(message)

    except Exception:
        log_id = get_log_id(user_id)
        logger.exception("Error start_handler %s", log_id)

        await update.message.reply_text(f"Произошла ошибка. Код ошибки для отладки {log_id}")


def register_base_handlers(application) -> None:
    application.add_handler(CommandHandler("start", start_handler))
