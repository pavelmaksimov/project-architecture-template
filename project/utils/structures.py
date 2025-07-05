import typing as t
from contextlib import contextmanager
from contextvars import ContextVar


class LazyInit[T]:
    def __init__(self, klass: type[T]):
        self._klass: type[T] = klass
        self._instance: T = None

    def __call__(self) -> T:
        if not self._instance:
            self._instance = self._klass()
        return self._instance

    def __getattr__(self, item):
        is_method = isinstance(getattr(self._klass, item), t.Callable)
        error = "Access to attributes and methods of this class is carried out through a class call."
        raise AttributeError(
            f"{error}\n{self._klass.__name__}.{item}() -> {self._klass.__name__}().{item}()"
            if is_method
            else f"{error}\n{self._klass.__name__}.{item} -> {self._klass.__name__}().{item}",
        )


class SafeLazyInit[T]:
    """
    Simple lazy initialization using contextvars instead of threading.local().

    Example:
        Settings = LazyContextVar(SettingsClass)
        instance = Settings()  # Creates instance lazily

        with Settings.local(param="value"):
            instance = Settings()  # Uses overridden parameters
    """

    def __init__(self, klass: type[T]):
        self._klass: type[T] = klass
        self._context_var: ContextVar[T | None] = ContextVar(f"{klass.__name__}_instance", default=None)

    def __call__(self) -> T:
        instance = self._context_var.get()
        if instance is None:
            instance = self._klass()
            self._context_var.set(instance)
        return instance

    @contextmanager
    def local(self, **kwargs):
        """Simple context manager for parameter overrides."""
        token = self._context_var.set(self._klass(**kwargs))

        try:
            yield
        finally:
            # Restore previous instance
            self._context_var.reset(token)
