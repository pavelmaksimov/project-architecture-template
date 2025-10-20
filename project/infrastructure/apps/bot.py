import logging

from llm_common.clients.telegram_client import TelegramHTTPXTransportWithMonitoring
from telegram.ext import AIORateLimiter, ApplicationBuilder
from telegram.request import HTTPXRequest

from project.domains.base.handlers import register_training_handlers
from project.settings import Settings

logger = logging.getLogger(__name__)


async def reminder_job(context):
    logger.info("Reminder job")


def run_bot_app() -> None:
    transport = TelegramHTTPXTransportWithMonitoring()
    httpx_request = HTTPXRequest(
        read_timeout=30,
        connect_timeout=30,
        httpx_kwargs={"transport": transport},
    )

    application_builder = (
        ApplicationBuilder()
        .token(Settings().TELEGRAM_BOT_TOKEN.get_secret_value())
        .request(httpx_request)
        .rate_limiter(AIORateLimiter(max_retries=3))
        .concurrent_updates(Settings().CONCURRENCY_LIMIT)
    )
    if Settings().is_any_stand():
        application_builder = application_builder.base_url(Settings().TELEGRAM_BASE_URL)
        application_builder = application_builder.base_file_url(
            Settings().TELEGRAM_FILE_BASE_URL,
        )

    application = application_builder.build()

    register_training_handlers(application)

    application.job_queue.run_repeating(reminder_job, interval=300, first=10)

    application.run_polling()


if __name__ == "__main__":
    run_bot_app()
