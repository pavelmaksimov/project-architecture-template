import logging
import time
import typing as t
from contextlib import contextmanager
from datetime import datetime


@contextmanager
def logging_disabled(level="CRITICAL"):
    logging.disable(getattr(logging, level))
    yield
    logging.disable(logging.NOTSET)


@contextmanager
def timer() -> t.Generator[t.Callable[[], float], t.Any, None]:
    """
    Example:

    with timer() as get_elapsed:
        time.sleep(1)
        print(f"Time has passed: {get_elapsed()} sec.")

        time.sleep(1)
        print(f"Time has passed: {get_elapsed()} sec.")
    """
    begin = time.perf_counter()
    yield lambda: round(time.perf_counter() - begin, 3)


@contextmanager
def timer_log(logger: logging.Logger, name: str = "", template: str = "{name}, {duration} sec."):
    begin = time.perf_counter()
    yield
    message = template.format(name=name or logger.name, duration=round(time.perf_counter() - begin, 3))
    logger.debug(message)


def get_log_id(user_id: int):
    return f"{datetime.now().strftime("%m%d%H%M%S")}{user_id}"
