import logging
import time
from contextlib import contextmanager


@contextmanager
def logging_disabled(level="CRITICAL"):
    logging.disable(getattr(logging, level))
    yield
    logging.disable(logging.NOTSET)


@contextmanager
def timer(logger: logging.Logger, name: str = "", template: str = "{name}, {duration} sec."):
    begin = time.perf_counter()
    yield
    message = template.format(name=name or logger.name, duration=round(time.perf_counter() - begin, 3))
    logger.info(message)
