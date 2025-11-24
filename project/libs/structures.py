import typing as t
from contextlib import contextmanager


class LazyInit[T]:
    """
    Simple lazy initialization using contextvars.

    Example:
        class SettingsValidation(pydantic.BaseModel):
            my_param: str = 1
        Settings = LazyInit(SettingsClass)

        assert Settings().my_param == "one"

        # Uses overridden parameters.
        with Settings.local(my_param="two"):
            assert Settings().my_param == "two
    """

    def __init__(self, klass: type[T], kwargs_func: t.Callable[[], dict] | None = None):
        self._klass: type[T] = klass
        self._kwargs_func: t.Callable[[], dict] = kwargs_func or (dict)
        self._instance: T = None  # type: ignore

    def __call__(self) -> T:
        if not self._instance:
            self._instance = self._klass(**self._kwargs_func())
        return self._instance

    def __getattr__(self, item):
        is_method = isinstance(getattr(self._klass, item), t.Callable)
        error = "Access to attributes and methods of this class is carried out through a class call."
        raise AttributeError(
            (
                f"{error}\n{self._klass.__name__}.{item}() -> {self._klass.__name__}().{item}()"
                if is_method
                else f"{error}\n{self._klass.__name__}.{item} -> {self._klass.__name__}().{item}"
            ),
        )

    @contextmanager
    def local(self, **kwargs):
        """Simple context manager for parameter overrides."""
        origin = self._instance

        try:
            self._instance = self._klass(**(self._kwargs_func() | kwargs))
            yield
        finally:
            # Restore previous instance
            self._instance = origin
