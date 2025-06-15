from typing import Callable


class LazyInit[T]:
    def __init__(self, klass: type[T]):
        self._klass: type[T] = klass
        self._instance: T = None

    def __call__(self) -> T:
        if not self._instance:
            self._instance = self._klass()
        return self._instance

    def __getattr__(self, item):
        is_method = isinstance(getattr(self._klass, item), Callable)
        error = "Access to attributes and methods of this class is carried out through a class call."
        raise AttributeError(
            f"{error}\n{self._klass.__name__}.{item}() -> {self._klass.__name__}().{item}()"
            if is_method
            else f"{error}\n{self._klass.__name__}.{item} -> {self._klass.__name__}().{item}"
        )
