import logging

from llm_common.prometheus import build_prometheus_metrics

from project.logger import setup_logging
from project.settings import Settings, MONITORING_APP_NAME, Envs

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if Settings().ENV == Envs.PROD:
        build_prometheus_metrics(project_name=MONITORING_APP_NAME, env="prod")
    elif Settings().ENV == Envs.LAMBDA:
        build_prometheus_metrics(project_name=MONITORING_APP_NAME, env="preprod")
    elif Settings().ENV == Envs.SANDBOX:
        build_prometheus_metrics(project_name=MONITORING_APP_NAME, env="dev")

    setup_logging(Settings().ENV)

    # Run apps.
