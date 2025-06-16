from typing import Any


def throw(exc: type[Exception], *args, **kwargs):
    raise exc(*args, **kwargs)


class AppError(Exception):
    pass


class NotFoundError(AppError, ValueError):
    def __init__(self, object_name: str, id: Any):
        super().__init__()
        self.object_name = object_name
        self.id = id

    def __str__(self):
        return f"{self.object_name}={self.id} not found"
