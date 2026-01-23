
# Антипаттерны
- хранить данные в файлах и в глобальных объектах, используйте базу данных, redis, postgres
- использовать pickle сериализацию, это не безопасно
- использовать для состояния ai агента просто словарь, надо минимум TypedDict, лучше pydantic схему, она с валидацией
- использовать одно состояния для всех агентов, это не безопасно, потому что при изменении поведения одного агента, 
  есть риск повлиять на другой
- Запрещено использовать Pandas, Polars и тому подобное.
  По опыту никто не может и не хочет разбираться в их апи, оно плохо читается, требуется знание их апи.
  Предпочтительнее язык SQL или операции над нативными объектами, списками и словарями, аннотированными через 
  TypedDict, dataclass и т.д.
- Связь Many-to-Many в ORM и БД через отдельную таблицу. Делайте через хранение идентификаторов в поля списках, без 
  промежуточной таблицы
- Запрещено добавлять логику на стороне БД, только на стороне приложения!


### Инъекция зависимостей
Видео про эту проблему https://www.youtube.com/watch?v=3Z_3yCgVKkM

**Плохо**: Создание зависимостей внутри классов или функций.
```python
class AskUseCase:
    def __init__(self):
        # Жесткая связка с реализацией, внутри этого класса, могут быть еще много зависимостей.
        self.chat = ChatService(...)

    def ask(self, user_id: int, question: str) -> str:
        # Тестирование потребует патча.
        repo = DatabaseRepository()  # прямое создание зависимости
        ...
```

При тестировании придется патчить все вложенные зависимости ChatService и DatabaseRepository:
```python
from unittes import mock

def test_ask():
    with mock.patch('path.to.ChatService'), \
        mock.patch('path.to.ChatService.create_answer'), \
        mock.patch('path.to.DatabaseRepository'):
        use_case = AskUseCase()
    ...
```

Такие тесты делают рефакторинг болезненным.
При изменении путей, имен объектов, потребуется вносить изменения во все тесты с патчами.
**Лучше такие зависимости проносить через аргументы методов, ниже будет пример.**

**Хорошо**: Внедрение зависимостей через контейнер зависимостей (DI Container):
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ... import Repository, ChatService

class AskUseCase:
    def __init__(
        self,
        repo: "Repository",
        chat: "ChatService",
    ):
        self.repo = repo
        self.chat = chat

    def ask(self, user_id: int, question: str) -> str:
        ...

class Repository:  # Реализация
    def get(self):
        pass

class ChatService:  # Реализация
    def create_answer(self, user_id, question):
        return "Answer"

class DIContainer:
    def __init__(self, repo=None, chat_service=None):
        self.repo = repo or Repository()
        self._chat = chat_service or ChatService()
        self.ask_use_case = AskUseCase(self.repo, self._chat)

container = DIContainer()
assert container.ask_use_case.ask(user_id=1, question="My question") == "Answer"

class OtherChatService:  # Другая реализация
    def create_answer(self, user_id, question):
        return "Other Answer"

other_container = DIContainer(chat_service=OtherChatService)
assert other_container.ask_use_case.ask(user_id=1, question="My question") == "Other Answer"
```

Такой класс можно тестировать с разными реализациями зависимостей без патчей:
```python
def test_ask_use_case():
    user_id = 1
    question_text = "Test question"
    expected_answer = "Test answer"

    class TestRepo:
        def get(self):
            return user_id

    class TestChatService:
        def create_answer(self, user_id, question):
            return expected_answer

    use_case = AskUseCase(
        repository=TestRepo(),
        chat=TestChatService(),
    )

    result = use_case.ask(user_id, question_text)

    assert result == expected_answer
```

**Преимущества подхода**:
1. Не требуется патчить внутренние зависимости
2. Явно видны все используемые зависимости и данные
3. Тест проверяет только публичное API класса
4. При рефакторинге внутренней реализации тест останется рабочим
