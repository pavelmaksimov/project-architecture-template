# Архитектурный шаблон для проекта

## Запуск
### Запуск приложения API
Нужно создать файл с обязательными параметрами `.env` в директории, откуда запускается `docker-compose` и запустить
приложение. Параметры определяются в [settings.py](project/settings.py).

### Разработка
#### Форматирование кода
Перед комитом запускайте форматирование кода [ruff](https://github.com/astral-sh/ruff).
Настройки форматирования в [pyproject.toml](pyproject.toml)

```bash
ruff format
#### Линтеры и Тесты
Перед комитом запускайте линтер [ruff](https://github.com/astral-sh/ruff).
Настройки линтера в [pyproject.toml](pyproject.toml)

ruff check --fix
mypy project
di-linter project
layers-linter project
pytest --cov=project tests/
```

Проверки сложности кода:
```bash
xenon --max-absolute B --max-modules B --max-average B -c project
radon mi --min C project
```

Следуйте [соглашению](https://www.conventionalcommits.org/en/v1.0.0/) именования комитов.

## Архитектурные границы

Основная цель слоистых архитектур - отделить бизнес-логику от фреймворков,
инфраструктуры и интерфейсов ввода/вывода.

Инфраструктура - это подключение к базе данных, ORM, обращение к внешнему сервису, шина сообщений, отправка
уведомлений, сбор метрик и т.д.

Главное правило - бизнес-логика не должна зависеть от деталей реализации и быть подальше от побочных эффектов.
Для этого нужно соблюдать правило инверсии зависимостей,
нижележащие слои не могут зависеть от вышестоящих.

Конкретно в Python это означает, что в слой бизнес-логики не должно быть импортов
из слоя инфраструктуры и ввода/вывода.
Чтобы обозначить ожидаемый интерфейс объектов из слоя инфраструктуры в аннотациях типов, не импортируя их,
можно создавать заглушки объектов наследуясь от класса `Protocol`.
Пример в [interfaces.py](project/domains/chat/interfaces.py)

Из-за того, что бизнес-логика не зависит от деталей реализации, упрощается тестирование.
Пример теста бизнес-логики посмотрите тут [test_ask.py](tests/test_domains/test_chat/test_ask.py)

Пример, как надо писать модули смотрите на примере домена [chat](project/domains/chat)

## Паттерны

Считаю, что абстракции UseCase, Service, Repository
могут быть достаточными для скрытия сложности на ранней стадии проекта.
Вводить новые сущности можно по мере увеличения сложности проекта.
Поэтому ограничимся описанием этих паттернов.

**UseCase** - точка входа в бизнес-сценарии. Пример [use_cases.py](project/domains/chat/use_cases.py).
Слой, через который интерфейсы ввода/вывода запускают бизнес-логику.
Здесь содержится валидация данных, авторизация, проверка квоты, лимитов и т.д.
Поэтому другие домены и поддомены бизнес-логики не должны использовать `UseCase`.
Реализация бизнес-процессов должна находится в `Service`-ах.
В `UseCase` не должно быть того, что потребуется в `Service`-ах в других доменах и поддоменах.
Имя сценария должно отражать бизнес-функцию.
Ожидается, что `UseCase` должен быть очень простым (мало строк) и понятным для чтения.
Сам код, нейминг классов и методов должен описывать, что происходит в терминах бизнеса -
провалидировать данные, проверить авторизацию, квоту, запустить бизнес-процесс.
Валидацию данных лучше использовать на этом слое,
но детали реализации (функции валидаций) выносить в модуль `validation.py`

`UseCase` - это объект без состояния.

**Service** - скрывает детали реализации бизнес-процесса. Пример [service.py](project/domains/chat/service.py)
Может объединять в себе работу одного или нескольких доменов.\
Объект без состояния.

**Repository** - нужны, чтобы отделить доступ к данным от ORM. Пример [repositories.py]
(project/domains/chat/repositories.py)\
Объект без состояния.

**Interface** - это объект, показывающий ожидаемый интерфейс, используется только в аннотациях типов.
Пример [interfaces.py](project/domains/chat/interfaces.py).
Избавляет от необходимости импорта реального объекта,
чтобы не нарушать правило инверсии зависимостей.

**Adapter** - реализация интерфейса. Пример [llm.py](project/infrastructure/adapters/llm.py).
Чтобы не зависеть от конкретных фреймворков и других зависимостей,
мы взаимодействуем с ними через фасад.
Благодаря этому можно заменить технологию, находящуюся за фасадом.

**DIContainer** - контейнер, в котором разрешаются зависимости, создается один раз.
Пример [container.py](project/container.py).
Знает кому, какие зависимости нужны и откуда их взять.
Избавляет нас от необходимости думать, как создать объект.
Если нужно в одной **транзакции** изменить несколько моделей, т.е. вне границ репозитория домена,
лучше создайте еще один репозиторий для этого.

## Структура проекта
Структура директорий не отражает слоистую архитектуру.
Модули объединяются по доменам (предметная область).
Так рекомендует `чистая архитектура` и `Domain Drive Design`.
Благодаря этому взглянув на структуру проекта, можно сразу понять, про что он.

- `project/domains` - модули относящиеся к доменам
- `project/infrastructure/adapters` - адаптеры к технологиям инфраструктуры
- `project/presentation` - приложения пользовательских интерфейсов
- `project/utils` - вспомогательные функции

Описание модулей:

Инфраструктура:
- [models.py](project/domains/chat/models.py) - модели данных ORM
- [endpoints.py](project/domains/chat/endpoints.py) - ресурсы и конечные точки API
- [repositories.py](project/domains/chat/repositories.py) - классы с доступом к данным
- `cli.py` - ресурсы интерфейса командной строки
- `handlers.py` - обработчики бота
- `exceptions.py` - исключения инфраструктуры

Бизнес-логика:
- [use_cases.py](project/domains/chat/use_cases.py) - бизнес сценарии
- [service.py](project/domains/chat/service.py) - реализация бизнес сценария
- [interfaces.py](project/domains/chat/interfaces.py) - интерфейсы, используются в аннотациях типов
- `validation.py` - валидация данных
- `exceptions.py` - исключения бизнес-сценариев

Можно использовать и в инфраструктуре и в бизнес-логике.
- [schemas.py](project/domains/chat/schemas.py) - схемы данных
- `enums.py` -

## Анти-паттерны
### Инъекция зависимостей
**Плохо**: Создание зависимостей внутри классов или функций.
```python
class AskUseCase:
    def __init__(self):
        # Жесткая связка с реализацией, внутри этого класса, могут быть еще много зависимостей.
        self.chat = ChatService(...)

    def ask(self, user_id: int, question: str) -> str:
        # Тестирование потребует моков.
        repo = DatabaseRepository()  # прямое создание зависимости
        ...
```

При тестировании придется мокать все вложенные зависимости ChatService и DatabaseRepository:
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
from typing import Protocol

class IRepository(Protocol):  # Интерфейс
    def get(self): ...

class IChatService(Protocol):  # Интерфейс
    def create_answer(self, user_id, question): ...

class AskUseCase:
    def __init__(
        self,
        repo: IRepository,   # Интерфейс вместо реализации
        chat: IChatService,  # Интерфейс вместо реализации
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

Такой класс можно тестировать с разными реализациями зависимостей без моков:
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

Видео про эту проблему https://www.youtube.com/watch?v=3Z_3yCgVKkM

## Фичи

### Проверка слоистой архитектуры с layers-linter
Проект использует [layers-linter](https://github.com/pavelmaksimov/layers-linter)
для автоматической проверки соблюдения архитектурных границ между слоями.

Конфигурация находится в файле [layers.toml](layers.toml), где определены:
- Слои приложения (dicontainer, usecases, services, repo, orm, adapters и т.д.)
- Модули, которые входят в каждый слой
- Направление зависимостей между слоями (перечисление разрешенных слоев для импорта для каждого слоя)
- Ограничения на использование некоторых внешних библиотек в слоях

Запуск проверки:
```bash
layers-linter project
```

Линтер анализирует импорты в коде и выявляет нарушения архитектурных границ:
1. Когда модуль из одного слоя импортирует модуль из слоя, от которого ему не разрешено зависеть
2. Когда модуль использует внешнюю библиотеку, которую для него не разрешено использовать

Это помогает поддерживать чистоту архитектуры и предотвращает появление нежелательных зависимостей между слоями.


### Проверка переусложнение кода
Используется метод "Цикломатическая сложность", через пакет [xenon](https://github.com/rubik/xenon),
замеряющий количество независимых путей через программу.
Встроен в [CI/CD](.gitlab-ci.yml)

```shell
xenon --max-absolute B --max-modules B --max-average B
```

Этот индекс говорит нам о том, насколько сложно будет поддерживать или редактировать кусок программы.
Этот параметр рассчитывается на основе Метрики Холстеда, через пакет [radon](https://github.com/rubik/radon/).

```shell
radon mi --min C project
```

Еще один линтер [wili](https://github.com/tonybaloney/wily) делает похожие вещи, может считать больше метрик,
показывать график изменений метрик во времени, анализируя историю комитов git.

Посмотреть изменение метрик после комита по сравнению с версией кода в ветке `master`,
через [wily](https://github.com/tonybaloney/wily).

```shell
wily build project
wily diff project -r master
```

Об этих метриках можно почитать в [тут](https://habr.com/ru/articles/456150/)

Этот инструмент на самом деле вычисляет, насколько сложным «выглядит» код,
а не насколько сложным он «является» на самом деле.

### Шаблон клиента для взаимодействия с внешними API
Находится в [base_client.py](project/utils/base_client.py)

### Логирование
Логи сохраняются в файлы в корне проекта в директорию `./logs`.
Настройки можно править в [logger.py](project/logger.py)

### Тестирование
Настроены фикстуры для создания сессий с БД и клиент API [conftest.py](tests/conftest.py).

Пример теста эндпоинта API [test_endpoints.py](tests/test_domains/test_chat/test_endpoints.py).

### Фабрики объектов модели ORM в тестах
Позволяют подготавливать окружение для тестирования.
Находятся в [factories.py](tests/factories.py)

Пример использования в [test_ask.py](tests/test_domains/test_chat/test_ask.py)

В тестах используется одна сессия SqlAlchemy с БД, поэтому объекты на самом деле не создаются фабрикой в БД, но
благодаря внутреннему хранилищу ORM, программа видит эти объекты.

Где обычно создают данные для теста? В фикстурах.
Потом их использует и в других тестах.
Чтоб создать немного другие данные, создает еще фикстуру и так проект ими зарастает.

Фабрики позволяют создавать объекты с разными параметрами, что делает их более гибкими.
Одна фабрика для создания объектов с разными настройками.
Полезно, когда вам нужно создавать объекты с разными состояниями в тестах.

Фабрики позволяют изолировать тесты друг от друга, так как каждый тест может создавать свои собственные объекты.

Фабрики упрощают поддержку кода, так как логика создания объектов сосредоточена в одном месте.
Если вам нужно изменить способ создания объекта, вы делаете это только в фабрике, а не в каждом тесте.

Фикстуры в `pytest` могут быть "магическими" — они автоматически подставляются в тесты,
что может затруднить понимание того, что именно происходит.
Фабрики, явно вызываются в коде, улучшая понимание теста.

Фабрики лучше подходят для сложных сценариев,
где нужно создавать объекты с множеством зависимостей или выполнять дополнительные действия при создании.
Фикстуры могут стать громоздкими в таких случаях.

### Миграции базы данных с Alembic
Проект использует [Alembic](https://alembic.sqlalchemy.org/) для управления миграциями базы данных.

#### Создание миграции
```bash
# Автоматически создать миграцию на основе изменений в моделях
alembic revision --autogenerate -m "Описание изменений"

# Или создать пустую миграцию
alembic revision -m "Описание изменений"
```

#### Применение миграций
```bash
# Применить все ожидающие миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1
```

Подробная документация по использованию Alembic находится в [alembic/README.md](alembic/README.md).

### Аутентификация по токену в API
Используйтся самая простая проверка, действует на все ресурсы, поэтому не думай об этом.
```python
def auth_by_token(auth_token: str = Header(alias="Access-Token")):
    if auth_token != Settings().ACCESS_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    return auth_token

app = FastAPI(..., dependencies=[Depends(auth_by_token)])
```


## API Best practices

### Формат ответов ресурсов API
Лучше возвращать в виде словаря.
При необходимости добавление новых данных в ответе ручки, нужно будет добавить только новое поле.
Используйте готовую схему для этого `project.domains.base.schemas.BaseResponse`.
Если указать в аргументе response_model, в swagger появится документация по выводу.
Но в случае тяжелых данных это может быть затратно по времени,
потому что данные буду провалидированы через `pydantic`.

```python
from project.domains.base.schemas import BaseResponse

@app.get("/my", response_model=BaseResponse[list[int]])
async def my_resource():
    return {"data": [1, 2]}
```

### Быстрая сериализация в JSON
 `ORJSONResponse` использует пакет `orjson` написанный на `RUST`, очень быстрый.
Можно указывать в самой ручке через аргумент `response_class`.

```python
from fastapi.responses import ORJSONResponse

@app.get("/health", response_class=ORJSONResponse)
async def health_check():
    return {}
```

### Версионирование
- Версионирование через URL путь `/user/v1/list`

Устаревшие ресурсы помечаем `deprecated`.
```
@app.get("/user/v1/list", deprecated=True)
```
