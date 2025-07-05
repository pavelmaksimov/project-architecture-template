import logging
import time
from contextlib import contextmanager
import typing as t


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
    elapsed = 0

    def update_elapsed():
        nonlocal elapsed
        elapsed = round(time.perf_counter() - begin, 3)
        return elapsed

    yield update_elapsed

    update_elapsed()  # di: skip


@contextmanager
def timer_log(logger: logging.Logger, name: str = "", template: str = "{name}, {duration} sec."):
    begin = time.perf_counter()
    yield
    message = template.format(name=name or logger.name, duration=round(time.perf_counter() - begin, 3))
    logger.debug(message)
