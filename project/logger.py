import logging.config
from pathlib import Path

from project.settings import Settings


def setup_logging():
    config = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": Settings().LOG_LEVEL,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "telegram": {
                "level": Settings().TELEGRAM_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "telegram.ext": {
                "level": Settings().TELEGRAM_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "apscheduler.scheduler": {
                "level": Settings().TELEGRAM_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "httpx": {
                "level": Settings().HTTP_REQUESTS_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "httpcore": {
                "level": Settings().HTTP_REQUESTS_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "openai": {
                "level": Settings().HTTP_REQUESTS_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "aiohttp": {
                "level": Settings().HTTP_REQUESTS_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "requests": {
                "level": Settings().HTTP_REQUESTS_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": Settings().SQLALCHEMY_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": Settings().SQLALCHEMY_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "redis": {
                "level": Settings().REDIS_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "flask": {
                "level": Settings().FLASK_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "werkzeug": {
                "level": Settings().FLASK_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {"level": Settings().LOG_LEVEL, "handlers": ["console"], "propagate": False},
    }

    if Settings().WRITE_LOGS_TO_FILE:
        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "app.log"

        config["handlers"]["file"] = {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": Settings().LOG_LEVEL,
            "formatter": "default",
            "filename": log_file,
            "when": "midnight",
            "backupCount": 14,
            "encoding": "utf8",
        }

        # Add file handler to all loggers
        for logger_config in config["loggers"].values():
            logger_config["handlers"].append("file")

        # Add file handler to root logger
        config["root"]["handlers"].append("file")

    logging.config.dictConfig(config)
