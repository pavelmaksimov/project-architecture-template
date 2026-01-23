"""
Модуль для создания машин состояний с валидацией переходов.

Предоставляет базовые классы и декораторы для реализации паттерна
"Машина состояний" (State Machine) с автоматической проверкой
допустимости переходов между состояниями.

Основные компоненты:
    - StateMachine: базовый класс для синхронных машин состояний
    - AsyncStateMachine: базовый класс для асинхронных машин состояний
    - transition: декоратор для синхронных переходов
    - atransition: декоратор для асинхронных переходов
    - TransitionError: исключение при недопустимом переходе

Пример использования (синхронный):
-------------------------------

    from enum import Enum
    from state_machine import StateMachine, transition, TransitionError

    # 1. Определяем состояния
    class OrderState(Enum):
        CREATED = "created"
        PAID = "paid"
        SHIPPED = "shipped"
        DELIVERED = "delivered"
        CANCELLED = "cancelled"

    # 2. Создаём машину состояний
    class Order(StateMachine):
        def __init__(self, order_id: str):
            self.order_id = order_id

        def get_state(self) -> OrderState:
            return ...

        def set_state(self, new_state: OrderState) -> None:
            ...

        # 3. Определяем переходы с помощью декоратора
        @transition(from_states=OrderState.CREATED, to_state=OrderState.PAID)
        def pay(self, amount: float) -> str:
            ...
            return f"Order {self.order_id} paid: ${amount}"

        @transition(from_states=OrderState.PAID, to_state=OrderState.SHIPPED)
        def ship(self) -> str:
            ...
            return f"Order {self.order_id} shipped"

        @transition(from_states=OrderState.SHIPPED, to_state=OrderState.DELIVERED)
        def deliver(self) -> str:
            ...
            return f"Order {self.order_id} delivered"

        # Переход из нескольких состояний
        @transition(
            from_states=[OrderState.CREATED, OrderState.PAID],
            to_state=OrderState.CANCELLED
        )
        def cancel(self, reason: str) -> str:
            ...
            return f"Order {self.order_id} cancelled: {reason}"

    # 4. Использование
    order = Order("ORD-001")
    print(order.get_state())          # OrderState.CREATED

    order.pay(99.99)
    print(order.get_state())          # OrderState.PAID

    order.ship()
    print(order.get_state())          # OrderState.SHIPPED

    # Попытка недопустимого перехода вызовет исключение
    try:
        order.cancel("changed mind")  # Нельзя отменить отправленный заказ!
    except TransitionError as e:
        print(e)  # Cannot call cancel from SHIPPED. Allowed states: CREATED, PAID


Пример использования (асинхронный):
----------------------------------

    import asyncio
    from enum import Enum
    from state_machine import AsyncStateMachine, atransition, TransitionError

    class TaskState(Enum):
        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"

    class AsyncTask(AsyncStateMachine):
        def __init__(self, task_id: str):
            self.task_id = task_id

        async def aget_state(self) -> TaskState:
            ...
            return self._state

        async def aset_state(self, new_state: TaskState) -> None:
            ...
            self._state = new_state

        @atransition(from_states=TaskState.PENDING, to_state=TaskState.RUNNING)
        async def start(self) -> str:
            ...
            return f"Task {self.task_id} started"

        @atransition(from_states=TaskState.RUNNING, to_state=TaskState.COMPLETED)
        async def complete(self, result: str) -> str:
            ...
            return f"Task {self.task_id} completed with: {result}"

        @atransition(from_states=TaskState.RUNNING, to_state=TaskState.FAILED)
        async def fail(self, error: str) -> str:
            ...
            return f"Task {self.task_id} failed: {error}"

    # Использование
    async def main():
        task = AsyncTask("TASK-001")
        print(await task.aget_state())    # TaskState.PENDING

        await task.start()
        print(await task.aget_state())    # TaskState.RUNNING

        await task.complete("success!")
        print(await task.aget_state())    # TaskState.COMPLETED

    asyncio.run(main())
"""

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
