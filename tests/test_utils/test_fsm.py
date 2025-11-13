from enum import auto, Enum

import pytest

from project.libs.fsm import transition, atransition, AsyncStateMachine, StateMachine, TransitionError


class TaskStatus(Enum):
    CREATED = auto()
    QUEUED = auto()
    IN_PROGRESS = auto()
    PAUSED = auto()  # Новое состояние для переключения
    FINISHED = auto()
    CANCELLED = auto()


class Task(StateMachine):
    """
    Пример реализации машины состояний с хранением состояния в памяти
    """

    def __init__(self, id: str):
        self.id = id
        self._status = TaskStatus.CREATED

    def get_state(self) -> TaskStatus:
        """Получить текущее состояние из памяти"""
        return self._status

    def set_state(self, new_state: TaskStatus) -> None:
        """Сохранить новое состояние в память"""
        self._status = new_state

    @property
    def status(self) -> TaskStatus:
        """Свойство для удобного доступа к состоянию"""
        return self.get_state()

    @transition([TaskStatus.CREATED], TaskStatus.QUEUED)
    def enqueue(self):
        return 1

    @transition([TaskStatus.QUEUED], TaskStatus.IN_PROGRESS)
    def process(self):
        return 2

    @transition([TaskStatus.CREATED, TaskStatus.QUEUED], TaskStatus.IN_PROGRESS)
    def prioritize(self):
        return 3

    @transition([TaskStatus.CREATED, TaskStatus.QUEUED, TaskStatus.IN_PROGRESS], TaskStatus.CANCELLED)
    def cancel(self):
        return 4

    @transition([TaskStatus.IN_PROGRESS], TaskStatus.FINISHED)
    def finish(self):
        return 5

    # Взаимные переходы PAUSED ⇄ IN_PROGRESS
    @transition([TaskStatus.IN_PROGRESS], TaskStatus.PAUSED)
    def pause(self):
        return 6

    @transition([TaskStatus.PAUSED], TaskStatus.IN_PROGRESS)
    def resume(self):
        return 7

    def __repr__(self):
        return f"Task(id={self.id}, status={self.status.name})"


class TestTaskTransitions:
    """Тесты для проверки всех переходов между состояниями"""

    def test_initial_state(self):
        """Тест начального состояния"""
        task = Task(id="test_1")

        assert task.status == TaskStatus.CREATED

    def test_enqueue_transition(self):
        """Тест перехода CREATED -> QUEUED"""
        task = Task(id="test_2")
        result = task.enqueue()

        assert result == 1
        assert task.status == TaskStatus.QUEUED

    def test_process_transition(self):
        """Тест перехода QUEUED -> IN_PROGRESS"""
        task = Task(id="test_3")
        task.enqueue()
        result = task.process()

        assert result == 2
        assert task.status == TaskStatus.IN_PROGRESS

    def test_prioritize_transition_from_created(self):
        """Тест перехода CREATED -> IN_PROGRESS через prioritize"""
        task = Task(id="test_4")
        result = task.prioritize()

        assert result == 3
        assert task.status == TaskStatus.IN_PROGRESS

    def test_prioritize_transition_from_queued(self):
        """Тест перехода QUEUED -> IN_PROGRESS через prioritize"""
        task = Task(id="test_5")
        task.enqueue()
        result = task.prioritize()

        assert result == 3
        assert task.status == TaskStatus.IN_PROGRESS

    def test_finish_transition(self):
        """Тест перехода IN_PROGRESS -> FINISHED"""
        task = Task(id="test_6")
        task.enqueue()
        task.process()
        result = task.finish()

        assert result == 5
        assert task.status == TaskStatus.FINISHED

    def test_cancel_from_created(self):
        """Тест отмены из CREATED"""
        task = Task(id="test_7")
        result = task.cancel()
        assert result == 4
        assert task.status == TaskStatus.CANCELLED

    def test_cancel_from_queued(self):
        """Тест отмены из QUEUED"""
        task = Task(id="test_8")
        task.enqueue()
        result = task.cancel()

        assert result == 4
        assert task.status == TaskStatus.CANCELLED

    def test_cancel_from_in_progress(self):
        """Тест отмены из IN_PROGRESS"""
        task = Task(id="test_9")

        task.enqueue()
        task.process()
        result = task.cancel()

        assert result == 4
        assert task.status == TaskStatus.CANCELLED

    def test_pause_resume_cycle(self):
        """Тест взаимных переходов PAUSED ⇄ IN_PROGRESS"""
        task = Task(id="test_10")

        task.enqueue()
        task.process()

        assert task.status == TaskStatus.IN_PROGRESS

        # Пауза
        result = task.pause()

        assert result == 6
        assert task.status == TaskStatus.PAUSED

        # Возобновление
        result = task.resume()

        assert result == 7
        assert task.status == TaskStatus.IN_PROGRESS

        # Снова пауза
        task.pause()
        assert task.status == TaskStatus.PAUSED

        # Снова возобновление
        task.resume()
        assert task.status == TaskStatus.IN_PROGRESS

    def test_multiple_pause_resume_cycles(self):
        """Тест множественных циклов пауза-возобновление"""
        task = Task(id="test_11")
        task.prioritize()  # IN_PROGRESS

        for _ in range(5):
            task.pause()

            assert task.status == TaskStatus.PAUSED

            task.resume()

            assert task.status == TaskStatus.IN_PROGRESS

        # После всех циклов можно завершить
        task.finish()

        assert task.status == TaskStatus.FINISHED

    def test_invalid_transition_process_from_created(self):
        """Тест недопустимого перехода: process из CREATED"""
        task = Task(id="test_12")

        with pytest.raises(TransitionError) as exc_info:
            task.process()

        assert "Cannot call process from CREATED" in str(exc_info.value)
        assert "QUEUED" in str(exc_info.value)

    def test_invalid_transition_pause_from_created(self):
        """Тест недопустимого перехода: pause из CREATED"""
        task = Task(id="test_13")

        with pytest.raises(TransitionError) as exc_info:
            task.pause()

        assert "Cannot call pause from CREATED" in str(exc_info.value)
        assert "IN_PROGRESS" in str(exc_info.value)

    def test_invalid_transition_resume_from_created(self):
        """Тест недопустимого перехода: resume из CREATED"""
        task = Task(id="test_14")

        with pytest.raises(TransitionError) as exc_info:
            task.resume()

        assert "Cannot call resume from CREATED" in str(exc_info.value)
        assert "PAUSED" in str(exc_info.value)

    def test_invalid_transition_finish_from_paused(self):
        """Тест недопустимого перехода: finish из PAUSED"""
        task = Task(id="test_15")
        task.enqueue()
        task.process()
        task.pause()

        with pytest.raises(TransitionError) as exc_info:
            task.finish()

        assert "Cannot call finish from PAUSED" in str(exc_info.value)
        assert "IN_PROGRESS" in str(exc_info.value)

    def test_finish_after_resume(self):
        """Тест успешного завершения после возобновления"""
        task = Task(id="test_16")
        task.enqueue()
        task.process()
        task.pause()
        task.resume()

        result = task.finish()

        assert result == 5
        assert task.status == TaskStatus.FINISHED


class TestStateMachineAbstract:
    """Тесты для проверки абстрактности StateMachine (синхронной версии)"""

    def test_cannot_instantiate_abstract_class(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            StateMachine()

    def test_cannot_instantiate_sync_state_machine(self):
        """Тест что нельзя создать экземпляр StateMachine напрямую"""
        with pytest.raises(TypeError):
            StateMachine()

    def test_must_implement_get_state(self):
        """Тест что необходимо имплементировать get_state"""

        class IncompleteStateMachine(StateMachine):
            def set_state(self, new_state):
                pass

        with pytest.raises(TypeError):
            IncompleteStateMachine()

    def test_must_implement_set_state(self):
        """Тест что необходимо имплементировать set_state"""

        class IncompleteStateMachine(StateMachine):
            def get_state(self):
                pass

        with pytest.raises(TypeError):
            IncompleteStateMachine()

    def test_backward_compatibility(self):
        """Тест что StateMachine является алиасом для StateMachine"""
        assert StateMachine is StateMachine


class TestAsyncStateMachineAbstract:
    """Тесты для проверки абстрактности AsyncStateMachine"""

    def test_cannot_instantiate_abstract_class(self):
        """Тест что нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            AsyncStateMachine()

    def test_must_implement_aget_state(self):
        """Тест что необходимо имплементировать aget_state"""

        class IncompleteAsyncStateMachine(AsyncStateMachine):
            async def aset_state(self, new_state):
                pass

        with pytest.raises(TypeError):
            IncompleteAsyncStateMachine()

    def test_must_implement_aset_state(self):
        """Тест что необходимо имплементировать aset_state"""

        class IncompleteAsyncStateMachine(AsyncStateMachine):
            async def aget_state(self):
                pass

        with pytest.raises(TypeError):
            IncompleteAsyncStateMachine()


class AsyncTask(AsyncStateMachine):
    """
    Пример реализации асинхронной машины состояний с асинхронными методами
    """

    def __init__(self, id: str):
        self.id = id
        self._status = TaskStatus.CREATED

    async def aget_state(self) -> TaskStatus:
        """Асинхронно получить текущее состояние из памяти"""
        return self._status

    async def aset_state(self, new_state: TaskStatus) -> None:
        """Асинхронно сохранить новое состояние в память"""
        self._status = new_state

    @property
    def status(self) -> TaskStatus:
        """Свойство для удобного доступа к состоянию (синхронное)"""
        return self._status

    @atransition([TaskStatus.CREATED], TaskStatus.QUEUED)
    async def enqueue(self):
        return 1

    @atransition([TaskStatus.QUEUED], TaskStatus.IN_PROGRESS)
    async def process(self):
        return 2

    @atransition([TaskStatus.CREATED, TaskStatus.QUEUED], TaskStatus.IN_PROGRESS)
    async def prioritize(self):
        return 3

    @atransition([TaskStatus.CREATED, TaskStatus.QUEUED, TaskStatus.IN_PROGRESS], TaskStatus.CANCELLED)
    async def cancel(self):
        return 4

    @atransition([TaskStatus.IN_PROGRESS], TaskStatus.FINISHED)
    async def finish(self):
        return 5

    @atransition([TaskStatus.IN_PROGRESS], TaskStatus.PAUSED)
    async def pause(self):
        return 6

    @atransition([TaskStatus.PAUSED], TaskStatus.IN_PROGRESS)
    async def resume(self):
        return 7

    def __repr__(self):
        return f"AsyncTask(id={self.id}, status={self.status.name})"


class TestAsyncTaskTransitions:
    """Тесты для проверки всех переходов между состояниями в асинхронных методах"""

    @pytest.mark.asyncio
    async def test_initial_state(self):
        """Тест начального состояния"""
        task = AsyncTask(id="async_test_1")

        assert task.status == TaskStatus.CREATED

    @pytest.mark.asyncio
    async def test_enqueue_transition(self):
        """Тест перехода CREATED -> QUEUED"""
        task = AsyncTask(id="async_test_2")

        result = await task.enqueue()

        assert result == 1
        assert task.status == TaskStatus.QUEUED

    @pytest.mark.asyncio
    async def test_process_transition(self):
        """Тест перехода QUEUED -> IN_PROGRESS"""
        task = AsyncTask(id="async_test_3")

        await task.enqueue()

        result = await task.process()

        assert result == 2
        assert task.status == TaskStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_prioritize_transition_from_created(self):
        """Тест перехода CREATED -> IN_PROGRESS через prioritize"""
        task = AsyncTask(id="async_test_4")

        result = await task.prioritize()

        assert result == 3
        assert task.status == TaskStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_prioritize_transition_from_queued(self):
        """Тест перехода QUEUED -> IN_PROGRESS через prioritize"""
        task = AsyncTask(id="async_test_5")

        await task.enqueue()

        result = await task.prioritize()

        assert result == 3
        assert task.status == TaskStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_finish_transition(self):
        """Тест перехода IN_PROGRESS -> FINISHED"""
        task = AsyncTask(id="async_test_6")

        await task.enqueue()
        await task.process()

        result = await task.finish()

        assert result == 5
        assert task.status == TaskStatus.FINISHED

    @pytest.mark.asyncio
    async def test_cancel_from_created(self):
        """Тест отмены из CREATED"""
        task = AsyncTask(id="async_test_7")

        result = await task.cancel()

        assert result == 4
        assert task.status == TaskStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_cancel_from_queued(self):
        """Тест отмены из QUEUED"""
        task = AsyncTask(id="async_test_8")

        await task.enqueue()

        result = await task.cancel()

        assert result == 4
        assert task.status == TaskStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_cancel_from_in_progress(self):
        """Тест отмены из IN_PROGRESS"""
        task = AsyncTask(id="async_test_9")

        await task.enqueue()
        await task.process()

        result = await task.cancel()

        assert result == 4
        assert task.status == TaskStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_pause_resume_cycle(self):
        """Тест взаимных переходов PAUSED ⇄ IN_PROGRESS"""
        task = AsyncTask(id="async_test_10")

        await task.enqueue()
        await task.process()

        assert task.status == TaskStatus.IN_PROGRESS

        # Пауза
        result = await task.pause()

        assert result == 6
        assert task.status == TaskStatus.PAUSED

        # Возобновление
        result = await task.resume()

        assert result == 7
        assert task.status == TaskStatus.IN_PROGRESS

        # Снова пауза
        await task.pause()

        assert task.status == TaskStatus.PAUSED

        # Снова возобновление
        await task.resume()

        assert task.status == TaskStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_multiple_pause_resume_cycles(self):
        """Тест множественных циклов пауза-возобновление"""
        task = AsyncTask(id="async_test_11")
        await task.prioritize()  # IN_PROGRESS

        for _ in range(5):
            await task.pause()

            assert task.status == TaskStatus.PAUSED

            await task.resume()

            assert task.status == TaskStatus.IN_PROGRESS

        # После всех циклов можно завершить
        await task.finish()

        assert task.status == TaskStatus.FINISHED

    @pytest.mark.asyncio
    async def test_invalid_transition_process_from_created(self):
        """Тест недопустимого перехода: process из CREATED"""
        task = AsyncTask(id="async_test_12")

        with pytest.raises(TransitionError) as exc_info:
            await task.process()

        assert "Cannot call process from CREATED" in str(exc_info.value)
        assert "QUEUED" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_transition_pause_from_created(self):
        """Тест недопустимого перехода: pause из CREATED"""
        task = AsyncTask(id="async_test_13")
        with pytest.raises(TransitionError) as exc_info:
            await task.pause()

        assert "Cannot call pause from CREATED" in str(exc_info.value)
        assert "IN_PROGRESS" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_transition_resume_from_created(self):
        """Тест недопустимого перехода: resume из CREATED"""
        task = AsyncTask(id="async_test_14")

        with pytest.raises(TransitionError) as exc_info:
            await task.resume()

        assert "Cannot call resume from CREATED" in str(exc_info.value)
        assert "PAUSED" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_transition_finish_from_paused(self):
        """Тест недопустимого перехода: finish из PAUSED"""
        task = AsyncTask(id="async_test_15")
        await task.enqueue()
        await task.process()
        await task.pause()

        with pytest.raises(TransitionError) as exc_info:
            await task.finish()

        assert "Cannot call finish from PAUSED" in str(exc_info.value)
        assert "IN_PROGRESS" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_finish_after_resume(self):
        """Тест успешного завершения после возобновления"""
        task = AsyncTask(id="async_test_16")
        await task.enqueue()
        await task.process()
        await task.pause()
        await task.resume()

        result = await task.finish()

        assert result == 5
        assert task.status == TaskStatus.FINISHED
