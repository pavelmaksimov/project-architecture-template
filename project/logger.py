import logging.config
from functools import lru_cache
from pathlib import Path


@lru_cache
def setup_logging(mode: str):
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "%(asctime)s [%(levelname)s] %(message)s"},
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "level": "ERROR",
                "formatter": "default",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "uvicorn": {"level": "INFO", "handlers": ["stdout"], "propagate": False},
            "uvicorn.error": {"level": "ERROR", "handlers": ["stdout", "stderr"], "propagate": False},
            "uvicorn.access": {"level": "INFO", "handlers": ["stdout"], "propagate": False},
            "uvicorn.asgi": {"level": "INFO", "handlers": ["stdout"], "propagate": False},
            "sqlalchemy.engine": {"level": "INFO", "handlers": ["stdout"], "propagate": False},
        },
        "root": {"level": "INFO", "handlers": ["stdout", "stderr"]},
    }

    if mode == "PROD":
        Path("logs").mkdir(parents=True, exist_ok=True)

        error_handler_name = "errors_file"
        config["handlers"][error_handler_name] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "default",
            "filename": "logs/error.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 1,
            "encoding": "utf8",
        }
        config["root"]["handlers"].append(error_handler_name)

        info_handler_name = "info_file"
        config["handlers"][info_handler_name] = {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "default",
            "filename": "logs/app.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 10,
            "encoding": "utf8",
            "delay": True,
        }
        config["root"]["handlers"].append(info_handler_name)

        # Добавляем файловые обработчики в специфические логгеры
        config["loggers"]["uvicorn"]["handlers"].append("info_file")
        config["loggers"]["uvicorn.error"]["handlers"].extend(["errors_file", "info_file"])
        config["loggers"]["uvicorn.access"]["handlers"].append("info_file")
        config["loggers"]["uvicorn.asgi"]["handlers"].append("info_file")
        config["loggers"]["sqlalchemy.engine"]["handlers"].append("info_file")

    logging.config.dictConfig(config)
