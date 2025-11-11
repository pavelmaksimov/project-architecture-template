import asyncio
import logging
import time

from llm_common.prometheus import build_prometheus_metrics

from project.infrastructure.apps.flask import run_api_app
from project.infrastructure.apps.bot import run_bot_app
from project.logger import setup_logging
from project.settings import Settings, MONITORING_APP_NAME, Envs

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if not MONITORING_APP_NAME:
        error = "MONITORING_APP_NAME cannot be empty"
        raise ValueError(error)

    if Settings().ENV == Envs.PROD:
        build_prometheus_metrics(project_name=MONITORING_APP_NAME, env="prod")
    elif Settings().ENV == Envs.LAMBDA:
        build_prometheus_metrics(project_name=MONITORING_APP_NAME, env="preprod")
    elif Settings().ENV == Envs.SANDBOX:
        build_prometheus_metrics(project_name=MONITORING_APP_NAME, env="dev")

    setup_logging()

    run_api_app()

    if Settings().is_any_stand():
        logger.info("Sleep 30 sec.")
        time.sleep(30)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    run_bot_app()
