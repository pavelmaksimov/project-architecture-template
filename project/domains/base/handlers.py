import logging

from llm_common.prometheus import action_tracking_decorator
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)

from project.infrastructure.utils.telegram import processing_errors, check_auth, timeout_with_retry

logger = logging.getLogger(__name__)


@timeout_with_retry
@processing_errors
@action_tracking_decorator("start_handler")
@check_auth
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = f"Привет {user_id}! Это пример обработчика Телеграм!"

    await update.message.reply_text(message)


def register_base_handlers(application) -> None:
    application.add_handler(CommandHandler("start", start_handler))
