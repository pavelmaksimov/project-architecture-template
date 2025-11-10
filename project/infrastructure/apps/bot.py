import asyncio
import logging

import uvloop
from llm_common.clients.telegram_client import TelegramHTTPXTransportWithMonitoring
from telegram.ext import AIORateLimiter, ApplicationBuilder
from telegram.request import HTTPXRequest

from project.domains.base.handlers import register_base_handlers
from project.settings import Settings

logger = logging.getLogger(__name__)


async def reminder_job(context):
    logger.info("Reminder job")


async def run_bot_app() -> None:
    transport = TelegramHTTPXTransportWithMonitoring()
    httpx_request = HTTPXRequest(
        httpx_kwargs={"transport": transport},
    )

    application_builder = (
        ApplicationBuilder()
        .token(Settings().TELEGRAM_BOT_TOKEN.get_secret_value())
        .request(httpx_request)
        .rate_limiter(AIORateLimiter(max_retries=3))
        .concurrent_updates(True)  # noqa: FBT003
    )
    if Settings().is_any_stand():
        application_builder = application_builder.base_url(Settings().TELEGRAM_BASE_URL)
        application_builder = application_builder.base_file_url(
            Settings().TELEGRAM_FILE_BASE_URL,
        )

    application = application_builder.build()

    register_base_handlers(application)

    application.job_queue.run_repeating(reminder_job, interval=300, first=10)

    async with application:
        await application.start()
        try:
            async with application.updater:
                await application.updater.start_polling()
                try:
                    # Требуется бесконечное ожидание, чтобы работал пулинг.
                    await asyncio.Event().wait()
                finally:
                    await application.updater.stop()
        finally:
            await application.stop()


if __name__ == "__main__":
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        runner.run(run_bot_app())
