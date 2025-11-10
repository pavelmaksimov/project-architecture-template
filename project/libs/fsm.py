import inspect
from abc import ABC, abstractmethod
from enum import Enum
from functools import wraps
from typing import Callable


class TransitionError(Exception):
    pass


class StateMachine(ABC):
    """
    Абстрактный базовый класс для синхронной машины состояний.

    Подклассы должны имплементировать методы получения и сохранения состояния.
    Это позволяет хранить состояние где угодно: в памяти, БД, Redis и т.д.
    """

    @abstractmethod
    def get_state(self) -> Enum:
        """
        Получить текущее состояние объекта.

        Returns:
            Текущее состояние как значение Enum
        """

    @abstractmethod
    def set_state(self, new_state: Enum) -> None:
        """
        Сохранить новое состояние объекта.

        Args:
            new_state: Новое состояние для сохранения
        """


class AsyncStateMachine(ABC):
    """
    Абстрактный базовый класс для асинхронной машины состояний.

    Подклассы должны имплементировать асинхронные методы получения и сохранения состояния.
    Это позволяет хранить состояние где угодно: в памяти, БД, Redis и т.д.
    """

    @abstractmethod
    async def aget_state(self) -> Enum:
        """
        Асинхронно получить текущее состояние объекта.

        Returns:
            Текущее состояние как значение Enum
        """

    @abstractmethod
    async def aset_state(self, new_state: Enum) -> None:
        """
        Асинхронно сохранить новое состояние объекта.

        Args:
            new_state: Новое состояние для сохранения
        """


def transition(from_states: list[Enum] | Enum, to_state: Enum):
    """
    Декоратор для определения допустимых переходов между состояниями.
    Используется для синхронных машин состояний (StateMachine).
    """
    if isinstance(from_states, Enum):
        from_states = [from_states]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self: StateMachine, *args, **kwargs):
            # Получаем текущее состояние через абстрактный метод.
            current_state = self.get_state()

            # Проверяем, находимся ли в одном из допустимых начальных состояний.
            if current_state not in from_states:
                allowed = ", ".join(str(s.name) for s in from_states)
                msg = f"Cannot call {func.__name__} from {current_state.name}. Allowed states: {allowed}"
                raise TransitionError(msg)

            result = func(self, *args, **kwargs)

            self.set_state(to_state)

            return result

        return wrapper

    return decorator


def atransition(from_states: list[Enum] | Enum, to_state: Enum):
    """
    Асинхронный декоратор для определения допустимых переходов между состояниями.
    Используется для асинхронных машин состояний (AsyncStateMachine).
    """
    if isinstance(from_states, Enum):
        from_states = [from_states]

    def decorator(func: Callable) -> Callable:
        # Проверяем, что декорируемая функция асинхронная
        if not inspect.iscoroutinefunction(func):
            msg = f"atransition can only decorate async functions, but {func.__name__} is not async"
            raise TypeError(msg)

        @wraps(func)
        async def wrapper(self: AsyncStateMachine, *args, **kwargs):
            # Получаем текущее состояние через асинхронный абстрактный метод.
            current_state = await self.aget_state()

            # Проверяем, находимся ли в одном из допустимых начальных состояний.
            if current_state not in from_states:
                allowed = ", ".join(str(s.name) for s in from_states)
                msg = f"Cannot call {func.__name__} from {current_state.name}. Allowed states: {allowed}"
                raise TransitionError(msg)

            result = await func(self, *args, **kwargs)

            await self.aset_state(to_state)

            return result

        return wrapper

    return decorator
