Файл генерируется автоматически из файлов в specs/rules/*

---

# Адаптеры (Adapters)

Адаптеры — это компоненты инфраструктурного слоя, 
которые инкапсулируют взаимодействие с внешними системами и сервисами.

**Расположение:** `project/infrastructure/adapters/`

**Основные принципы:**
- Изолируют внешние зависимости от бизнес-логики
- Предоставляют удобный интерфейс для работы с внешними сервисами
- Обрабатывают ошибки и специфику внешних API
- Упрощают замену внешних зависимостей на другие, в случае необходимости
- Позволяют подменять реализацию адаптера в тестах на заглушки

## Существующие адаптеры

### auth.py — Адаптер аутентификации

Адаптер для работы с сервисом аутентификации пользователей.
Запросы отслеживаются через prometheus.

**Основной функционал:**
- `check_telegram_user(user_telegram_id: int) -> bool` — проверка существования пользователя Telegram
- `get_users_data() -> dict` — получение данных всех пользователей

### keycloak.py — Адаптер Keycloak

Адаптер для интеграции с Keycloak (система управления идентификацией и доступом).

### voice.py — Адаптер транскрибации и синтеза речи

**⭐ Качественное решение, проверенное на практике**

Адаптер для работы с голосовыми данными: преобразование речи в текст (STT) и текста в речь (TTS).

**Реализация:** `VoiceAdapter` — использует OpenAI API

**Основной функционал:**
- `voice_to_text(voice: bytes | bytearray) -> str` — преобразование голоса в текст
  - Поддерживает указание языка (по умолчанию `ru`)
- `text_to_voice(text: str, instructions: str, voice: str = "alloy") -> io.BytesIO` — синтез речи из текста

**Особенности:**
- Использует retry-механизм с исключением определенных ошибок (BadRequestError, RateLimitError и др.)
- Интегрирован с Prometheus через декораторы `@action_tracking_decorator`
- Оптимизирован для работы с Telegram (поддержка `download_as_bytearray()`)

**Пример использования:**
```python
# Для Telegram
ogg_data = await voice_file.download_as_bytearray()
text = await voice_adapter.voice_to_text(ogg_data)
```

### llm.py — Адаптер для работы с LLM

**Основной функционал:**
- `llm_chat_client() -> ChatOpenAI` — создание клиента LangChain для чата
- `llm_aclient() -> AsyncClient` — создание асинхронного OpenAI клиента

**Особенности:**
- Поддержка Prometheus мониторинга
- Поддержка middleware proxy для работы в контуре

### database.py / adatabase.py — Адаптеры базы данных

Адаптеры для работы с базой данных (синхронный и асинхронный варианты).

**Основной функционал:**
- Управление соединениями с БД
- Выполнение запросов
- Управление транзакциями

TODO: примеры использования сессий и транзакций

### cache.py / acache.py — Адаптеры к Redis

Адаптеры для работы с системой кеширования (синхронный и асинхронный варианты).

**Основной функционал:**
- Сохранение и получение данных из кеша
- Управление TTL (время жизни)
- Инвалидация кеша

---

# Создание миграций базы данных Alembic
Проект использует [Alembic](https://alembic.sqlalchemy.org/) для управления миграциями базы данных.

#### Создание миграций
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

При переключение веток не забудьте откатывать миграции, если в ваших ветках они ушли дальше, чем на ветке, в которую 
вы переключились.

Подробная документация по использованию Alembic находится в [alembic/README.md](alembic/README.md).

---

# Антипаттерны
- хранить данные в файлах и в глобальных объектах, используйте базу данных, redis, postgres
- использовать pickle сериализацию, это не безопасно
- использовать для состояния агента просто словарь, минимум TypedDict, лучше pydantic
- использовать одно состояния для всех агентов, это не безопасно, потому что при изменении поведения одного агента 
  есть риск повлиять на другой
- Запрещено использовать Pandas, Polars и тому подобное.
  По опыту никто не может и не хочет разбираться в их апи, оно плохо читается, требуется знание их апи.
  Предпочтительнее язык SQL или операции над нативными объектами, списками и словарями, аннотированными через 
  TypedDict, dataclass и т.д. 


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

---

# Автотесты
- Как запускать тесты написанно в [README.md](../../README.md)
- Фикстуры в [conftest.py](tests/conftest.py).
- При запуске тестов автоматически поднимаются контейнеры с базами данных через testconteiners (на время тестов)
- Уровень логирование в тестах настраивается в [pytest.ini](pytest.ini)

Пример теста эндпоинта API [test_endpoints.py](tests/test_domains/test_chat/test_endpoints.py).

##  Антипаттерны в тестах
- абстракции для тестов, это последнее, во что хочется вникать, максимально избегайте их. Идеально, когда всё, что 
  относится к данному тесту, находится внутри него, без необходимости прыгать по модулям, чтоб понять, как он 
  работает.
- данные для теста в фикстурах затрудяет чтение теста, добавление и изменение данных. Данные 
  должны быть внутри теста, несмотря на то, что данные могут дублироваться между тестами.
- большое кол-во assert в тесте это плохо, скорее всего в тамком тесте проверяется много кейсов, наилучший вариант, 
  в одном тесте проверять что-то одно
- не пишите юнит-тесты, потому что при рефакторинге приходится изменять тесты, а этим ни кто не хочет 
  заниматься, поэтому будет затруднять рефакторинг. Тестируйте поведение программы. Тестируйте сверху, через UseCase 
  или эндпоинты. Пишите функциональные тесты.
- запрещено использовать unittest.mock.patch, если он вам понадобился, значит реализация спроектирована неверно, 
  перепишите код, следуя принципу dependency inversion. Подмените реализацию объекта, передав мок объект с другим 
  поведением (заглушку) в конструктор или через аргументы функции.
- проверяйте в тестах поведение программы, а не объекты

## Как создавать данные для теста

В проекте есть фабрики объектов ORM моделей, они позволяют подготавливать окружение для тестирования.
Находятся в [factories.py](tests/factories.py).
Пример использования в [test_ask.py](tests/test_domains/test_chat/test_ask.py).

В тестах используется одна сессия SqlAlchemy с БД без завершения транзакции, поэтому объекты на самом деле не создаются 
фабрикой в БД, но благодаря внутреннему хранилищу ORM, программа видит эти объекты.

Где обычно создают данные для теста? В фикстурах.
Потом их использует и в других тестах.
Чтоб создать немного другие данные, создает еще фикстуру и так проект ими зарастает.

Фабрики позволяют создавать объекты с разными параметрами, что делает их более гибкими.
Одна фабрика для создания объектов с разными настройками.
Полезно, когда вам нужно создавать объекты с разными состояниями в тестах.

Фабрики позволяют изолировать данные тестов друг от друга, так как каждый тест может создавать свои собственные объекты.

Фабрики упрощают поддержку кода, так как логика создания объектов сосредоточена в одном месте.
Если вам нужно изменить способ создания объекта, вы делаете это только в фабрике, а не в каждом тесте.

Фикстуры в `pytest` могут быть "магическими" — они автоматически подставляются в тесты,
что может затруднить понимание того, что именно происходит.
Фабрики, явно вызываются в коде, улучшая понимание теста.

Фабрики лучше подходят для сложных сценариев,
где нужно создавать объекты с множеством зависимостей или выполнять дополнительные действия при создании.
Фикстуры могут стать громоздкими в таких случаях.

## Описание фикстур в conftest.py

### Фикстуры настройки окружения

**`setup`** (scope="session", autouse=True)
- Автоматически применяется ко всем тестам
- Устанавливает тестовое окружение (ENV="TEST", токены, ключи)
- Настраивает логирование

### Фикстуры для работы с базой данных

**`init_database`** (scope="session")
- Поднимает PostgreSQL контейнер через testcontainers
- Создает схему БД
- Возвращает engine для подключения
- Автоматически очищается после всех тестов

**`session`**
- Создает синхронную сессию SQLAlchemy для теста
- Все изменения откатываются после теста (rollback)
- БД всегда остается чистой между тестами

Пример использования:
```python
def test_create_user(session):
    # После теста данные автоматически откатятся
    ...
```

**`asession`**
- Асинхронная версия `session`

Пример использования:
```python
async def test_create_user_async(asession):
    # После теста данные автоматически откатятся
    ...
```

### Фикстуры для работы с Redis

**`init_redis`** (scope="session")
- Поднимает Redis контейнер
- Возвращает синхронный клиент Redis

**`redis`**
- Синхронный Redis клиент для теста
- Автоматически очищает базу после теста (flushdb)

Пример использования:
```python
def test_cache(redis):
    # После теста Redis очищается
    ...
```

**`async_init_redis`** (scope="session")
- Асинхронная версия Redis контейнера

**`async_redis`**
- Асинхронный Redis клиент
- Очищается после теста

Пример использования:
```python
async def test_cache_async(async_redis):
    # После теста Redis очищается
    ...
```

### Фикстуры для тестирования API

**`api_client`**
- TestClient для тестирования FastAPI эндпоинтов
- Автоматически добавляет API токен в заголовки

Пример использования:
```python
def test_endpoint(api_client):
    response = api_client.get("/api/users")
    assert response.status_code == 200
    assert response.json() == []
```

### Фикстуры для мокирования HTTP запросов

**`responses`**
- Для мокирования синхронных HTTP запросов (httpx)
- Использует библиотеку respx

Пример использования:
```python
def test_external_api(responses):
    responses.add(
        responses.GET,
        "https://api.example.com/data",
        json={"result": "success"},
        status=200
    )
    # Теперь запросы на этот URL вернут mock-ответ
```

**`aresponses`**
- Для мокирования асинхронных HTTP запросов (aiohttp)
- Использует библиотеку aioresponses

Пример использования:
```python
async def test_external_api_async(aresponses):
    aresponses.add(
        "https://api.example.com/data",
        method="GET",
        payload={"result": "success"},
        status=200
    )
    # Асинхронные запросы на этот URL вернут mock-ответ
```

### Фикстуры для работы с Keycloak

**`keycloak_client`**
- Синхронный клиент Keycloak с тестовыми настройками
- Для тестирования интеграции с Keycloak

**`mock_keycloak`**
- Мокирует ответы Keycloak для синхронных запросов
- Возвращает тестовый токен

Пример использования:
```python
def test_keycloak_auth(keycloak_client, mock_keycloak):
    # mock_keycloak автоматически мокирует запросы
    token = keycloak_client.get_token()
    assert token == "test_token"
```

**`keycloak_aclient`**
- Асинхронный клиент Keycloak

**`mock_async_keycloak`**
- Мокирует асинхронные запросы к Keycloak

### Вспомогательные фикстуры

**`project_dir`** (scope="session")
- Возвращает путь к директории проекта
- Полезно для работы с файлами проекта в тестах

Пример использования:
```python
def test_config_file(project_dir):
    config_path = project_dir / "config.yaml"
    assert config_path.exists()
```

---

# Как добавить адаптер к внешней системе

Для создания адаптеров, работающих с внешними HTTP API, используйте классы из [base_client.py](../../project/infrastructure/utils/base_client.py).

**Основные компоненты:**

1. **AsyncApi** — базовый класс для асинхронных HTTP клиентов
   - Поддерживает context manager для управления сессиями
   - Автоматическая обработка ошибок (4xx, 5xx)
   - Интеграция с Prometheus метриками
   - Логирование запросов и ответов

2. **SyncApi** — базовый класс для синхронных HTTP клиентов
   - Аналогичный интерфейс с AsyncApi
   - Подходит для синхронного кода

3. **IClient** — Protocol, определяющий интерфейс клиента
   - Определяет структуру клиентского класса
   - Обеспечивает единообразие адаптеров

### Пошаговая инструкция по созданию адаптера

#### Шаг 1: Создать файл адаптера

Создайте новый файл в `project/infrastructure/adapters/`, например `my_service.py`.

#### Шаг 2: Определить кастомные классы ошибок (опционально)

```python
from project.exceptions import ApiError, ServerError, ClientError

class MyServiceApiError(ApiError):
    pass

class MyServiceServerError(ServerError):
    pass

class MyServiceClientError(ClientError):
    pass
```

#### Шаг 3: Создать класс адаптера

**Вариант А: Асинхронный адаптер**

```python
from project.infrastructure.utils.base_client import AsyncApi, IClient

class MyServiceClient(IClient):
    class Api(AsyncApi):
        ApiError = MyServiceApiError
        ServerError = MyServiceServerError
        ClientError = MyServiceClientError
        # Опционально: кастомная сессия для мониторинга
        # ClientSession = MyCustomHttpClient

    def __init__(self, api_key: str):
        self.api_root = "https://api.myservice.com"
        self.api = self.Api(
            self.api_root,
            name_for_monitoring="my_service_api",
            headers={"Authorization": f"Bearer {api_key}"},
            request_settings={"timeout": 30},
        )

    async def get_items(self, resource_id: str) -> dict:
        """Получить данные ресурса."""
        return await self.api.call_endpoint(
            f"path/to/resource/{resource_id}",
            method="GET",
            request_settings={"timeout": 3} # example timeout for resource
        )

    async def create_items(self, data: dict) -> dict:
        """Создать новый ресурс."""
        return await self.api.call_endpoint(
            "path/to/resource/",
            method="POST",
            json=data,
        )
```

**Вариант Б: Синхронный адаптер**

```python
from project.infrastructure.utils.base_client import SyncApi

class MyServiceSyncClient:
    class Api(SyncApi):
        ApiError = MyServiceApiError
        ServerError = MyServiceServerError
        ClientError = MyServiceClientError

    def __init__(self, api_key: str):
        self.api_root = "https://api.myservice.com"
        self.api = self.Api(
            self.api_root,
            name_for_monitoring="my_service_api",
            headers={"Authorization": f"Bearer {api_key}"},
        )

    def get_items(self, resource_id: str) -> dict:
        return self.api.call_endpoint(
            f"resources/{resource_id}",
            method="GET",
        )
```

#### Шаг 4: Добавить фабричный метод (опционально) для ленивой инициализации

```python
from functools import cache
from project.settings import Settings

@cache
def my_service_client():
    return MyServiceClient(
        api_key=Settings().MY_SERVICE_API_KEY.get_secret_value()
    )
```

#### Шаг 5: Использование адаптера

```python
from project.infrastructure.adapters.my_service import my_service_client

client = my_service_client()
data = await client.get_items("123")

# С переиспользованием сессии (для множественных запросов)
async with client.api.Session():
    data1 = await client.get_items("123")
    data2 = await client.get_items("456")
    # Сессия будет переиспользована
```

### Расширенные возможности

#### Кастомная обработка ответов

Если нужна специфическая обработка ответов, переопределите методы в Api классе:

```python
class LimitError(MyServiceClientError):
    pass

class MyServiceClient(IClient):
    class Api(AsyncApi):
        async def response_to_native(self, response):
            # Кастомная десериализация
            return await super().response_to_native(response)
        
        async def error_handling(self, response, response_data):
            # Кастомная обработка ошибок
            if response.status == 429:
                raise LimitError("LimitError: Too many requests.")
            
            return await super().error_handling(response, response_data)
```

#### Retry-механизм

Для критичных операций добавьте retry:

```python
from project.libs.retry import retry_on_exception

class MyServiceClient(IClient):
    # ... (определение Api класса)

    @retry_on_exception(
        (LimitError,),
        max_attempts=3,
        backoff=2,
    )
    async def create_item(self, data: dict):
        ...
```

---

# Управление сессиями базы данных (Database Sessions)

**Расположение:** `project/infrastructure/adapters/adatabase.py`

### asession() — Управление сессиями

**Для чтения данных**. Переиспользует существующую сессию или создает новую.

```python
# Простое чтение
async with asession() as session:
    result = await session.execute(select(User).where(User.id == user_id))
    user = resulscalar_one_or_none()

# Вложенные вызовы используют ту же сессию
async with asession() as session1:
    async with asession() as session2:
        # session1 === session2
```

⚠️ **Не создает транзакцию**. Для изменений используйте `atransaction()`.

---

### atransaction() — Управление транзакциями

**Для изменения данных**. Создает транзакцию с автоматическим commit/rollback.

```python
# Простая транзакция
async with atransaction() as session:
    user = User(name="John")
    session.add(user)
# Автоматический commit

# Вложенные транзакции создают SavePoint
async with atransaction() as session:
    user = User(name="John")
    session.add(user)
    
    try:
        async with atransaction() as s:
            # Создается SavePoint
            post = Post(title="Test", user=user)
            s.add(post)
            raise ValueError()
    except ValueError:
        pass  # SavePoint откатился, но user сохранится
```

**Поведение при вложенности:**
- Сессия в транзакции → создает `begin_nested()` (SavePoint)
- Сессия без транзакции → создает `begin()`
- Нет сессии → создает сессию и транзакцию

---

### current_atransaction() — Текущая или новая транзакция

**Для переиспользуемых функций**. Возвращает активную транзакцию или создает новую.

```python
async def reusable_operation():
    async with current_atransaction() as session:
        # Работает и внутри, и вне существующей транзакции
        user = User(name="John")
        session.add(user)

# Вариант 1: создаст транзакцию
await reusable_operation()

# Вариант 2: использует существующую
async with atransaction():
    await reusable_operation()
```

**Отличие от atransaction():**
- `atransaction()` — всегда создает новый уровень (SavePoint)
- `current_atransaction()` — переиспользует текущую транзакцию без SavePoint

---

## Использование сессий и транзакций в классах репозиториях

**Расположение:** `project/domains/base/repositories.py`

### ORMRepository — Базовый класс репозиториев

Дает доступ к открытие сессии и транзакции.
Область применения, внутри методов классов,
во вне лучше использовать обертки через project.container.AllRepositories

Вне классов, их использовать не надо!

```python
class ORMRepository(Generic[T]):
    @classmethod
    @contextmanager
    def get_session(cls):
        with Session() as session:
            yield session

    @classmethod
    @contextmanager
    def get_transaction(cls):
        with transaction() as session:
            yield session

    @classmethod
    @contextmanager
    def get_current_transaction(cls):
        with current_transaction() as session:
            yield session


class ORMModelRepository(ORMRepository[T]):
    # Наследует методы от ORMRepository.
    ...
```

---

## Использование через контейнер

### AllRepositories — Точка доступа к репозиториям

**Расположение:** `project/container.py`

Класс `AllRepositories` предоставляет централизованный доступ к транзакциям.
Его надо использовать, когда на уровне бизнес-логики
нужно обернуть вызов методов из нескольких репозиториев.

```python
class AllRepositories:
    def __init__(self):
        self.user = UserRepository()
        ...

    @classmethod
    @contextmanager
    def transaction(cls) -> Generator["ORMSession", Any, None]:
        with transaction() as session:
            yield session

    @classmethod
    @contextmanager
    def current_transaction(cls) -> Generator["ORMSession", Any, None]:
        with current_transaction() as session:
            yield session
```

**Использование:**

```python
from project.container import Repositories

# Через экземпляр репозитория
user = Repositories().user.get(user_id)

# Через контейнер транзакций
with Repositories.transaction() as session:
    Repositories.user.save(user_data)
    Repositories.employee.save(employee_data)

# Переиспользование текущей транзакции
with Repositories.current_transaction() as session:
    ... 
```

---

## Использование в тестах

В `tests/conftespy` определены фикстуры с автоматическим rollback:

### Синхронная фикстура session

```python
@pytesfixture
def session(init_database):
    with database.Session() as session:
        with session.begin() as t:
            with session.begin_nested():
                yield session
                # Данные откатываются после теста
            rollback()
    
    database.engine_factory.cache_clear()
    database.scoped_session_factory.cache_clear()
```

### Асинхронная фикстура asession

```python
@pytest_asyncio.fixture
async def asession(init_database):
    async with adatabase.asession() as asession:
        async with asession.begin() as t:
            async with asession.begin_nested():
                yield asession
                # Данные откатываются после теста
            await rollback()
    
    adatabase.aengine_factory.cache_clear()
    adatabase.async_sessionmaker_factory.cache_clear()
```

**Как это работает:**
1. Открывается сессия через `adatabase.asession()`
2. Создается основная транзакция через `begin()`
3. Создается вложенная транзакция (SavePoint) через `begin_nested()`
4. Тест работает внутри SavePoint
5. После теста данные откатываются через `rollback()`
6. Очищаются кеши фабрик для изоляции между тестами

Это обеспечивает чистую БД для каждого теста без необходимости пересоздания схемы.

---

# Exceptions
Свои собственные исключения наследуйте от `project.exceptions.AppError`

---

## API Best practices
uvicorn запускается с циклом uvloop
```bash
uvicorn project.presentation.api:app -host 0.0.0.0 --loop uvloop
```

Эндпоинты должны располагаться в `project.domains.{name}.endpoints`.

### Формат ответов ресурсов API
Лучше возвращать в виде словаря.
Тогда при необходимости добавление новых данных в ответе ручки, нужно будет добавить только новое поле.
Используйте готовую схему для этого `project.domains.base.schemas.BaseResponse`.
Если указать в аргументе response_model, в swagger появится документация по выводу.
Но в случае тяжелых данных это может быть затратно по времени,
потому что данные буду валидироваться через `pydantic`, это замедляет 2.5 раза по сравнению с обычным dict/dataclass.

```python
from project.domains.base.schemas import BaseResponse

@app.get("/my", response_model=BaseResponse[list[int]])
async def my_resource():
    return {"data": [1, 2]}
```

### Аутентификация по токену в API
Проверка уже зашита в эндпоинты.
```python
def auth_by_token(auth_token: str = Header(alias="Api-Token")):
    if auth_token != Settings().API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    return auth_token

app = FastAPI(..., dependencies=[Depends(auth_by_token)])
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
- Изменение ручек делаем через добавление новой ручки с новой версией, а предыдущую помечаем `deprecated`.
```
@app.get("/user/v1/list", deprecated=True)
```

### Ошибки HTTP
Не нужно тащить `fastapi.exceptions.HTTPException` в бизнес-логику, они должны оставаться в модулях `endpoints.py`.

---

# Архитектурные границы

TODO: переработать

Основная цель слоистых архитектур - отделить бизнес-логику от фреймворков, инфраструктуры и интерфейсов ввода/вывода.

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

## Слои

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

- доступ к данным изолируйте в классах Repository, в бизнес-логике извлечение данных из бд затрудняет 
  читать и понимать саму бизнес-логику. Ищите примеры в модулях [repositories.py](project/domains/user/repositories.py)
- Есть generic базовый класс с базовыми методами, наследуйте ваши Repository от него, пример в [repositories.py](project/domains/user/repositories.py)

```python
# Когда мы смотрим на бизнес-логику, лучше увидеть такое
UserRepo.get_users(user_ids=[1, 2, 3])
# чем такое
query = select(User).where(User.id.in_([1, 2, 3]))
async with Session() as session:
    result = session.execute(query)
    data = await result.scalars().all()
```

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

## Линтер слоев
Есть линтер, который проверяет направление зависимостей, настроенных в конфиге [layers.toml](../../layers.toml).
Запускается через 
```bash
layers-linter project
```

---

# Не создавайте глобальные объекты

глобальные объекты это топ антипаттерн, далующий программу крайне плохой (TODO: написать подробнее почему).

Вместо них создавайте объекты с ленивой инициализацией (в момент реального использования объекта)

Самый простой и частый вариант это создать фнукцию с кешом.
Там где используете клиент, вы вызываете эту функцию и получаете объект, это позволяет отложить инициализацию до 
момента реально использования.

```python
from functools import cache
from langchain_openai import ChatOpenAI
from project.settings import Settings

@cache
def client():
    return ChatOpenAI(
        api_key=Settings().LLM_API_KEY.get_secret_value(),
    )

async def llm_logic():
    result = await client().ainvoke()
```

Если в тестах нужно инициализировать объект с другими параметрами, тогда можете использовать
`LazyInit` из [structures.py](project/libs/structures.py), он предоставляют механизм ленивой инициализации и 
контекстный менеджер для инициализации объекта с другими параметрами.

Пример такого использования для класса [Settings](project/settings.py), который под капотом получает переменные 
окружения, а в тестах мы хотим заменять переменные окружения.

```python
# ✅ ПРАВИЛЬНО - объявление класса
class MyServiceClass:
    def __init__(self, param):
        self.param = param
        
    def do_something(self):
        return self.param

MyService = LazyInit(MyServiceClass, kwargs_func=lambda: {"param": Settings().PARAM})

# ❌ НЕПРАВИЛЬНО - инициализация в глобальной области
result = MyService().do_something()

# ❌ НЕПРАВИЛЬНО - сохранение экземпляра в глобальной области
my_service = MyService()  # ❌ ПЛОХО
my_service.do_something()

# ✅ ПРАВИЛЬНО - сохранение в атрибутах экземпляра допускается, потому что экземпляр создается лениво.
class MyClass:
    def __init__(self):
        self.adapter = GitLabAdapter()
        
# ✅ ПРАВИЛЬНО - Вызов внутри функции будет инициализироваться лениво
def myfunc():
    x = MyService().do_something()
```

---

# Запуск линтеров

- ruff check --fix (линтер)
- ruff format (форматирование)
- di-linter (проверка инъекций зависимостей)
- la-linter (проверка архитектурных слоев)
- обновление requirements.txt через UV

## Проверка слоистой архитектуры с layers-linter
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

---

# Мониторинг

Есть готовые настроенные дашборды для метрик собираемых в этом проекте через Prometheus.
Можно узнать у коллег разработчиков и девопсов.
Также на эти метрики в дашбордах можно настроить алерты в телеграм

Для критичных секций кода.
Для Telegram обработчиков и callback если это telegram бот.

## Отслеживание времени и статуса выполнения секций кода

Для этого есть контекстный менеджер и декоратор.

Чтобы эти примитивы смогли отследить возниклования exception, внутри этих контекстного менеджера и декоратора не должны
подавляться exception.

```python
from llm_common.prometheus import action_tracking, action_tracking_decorator

# Использование контекст-менеджера
with action_tracking("data_processing") as tracker:
    # Ваш код
    processed_data = process_data()
    # Опционально: трекинг размера данных
    tracker.size(len(processed_data))
    
    # Опционально: зафиксировать, как ошибку
    tracker.to_fail()

# Использование декоратора
@action_tracking_decorator("myfeature_llm_call")
async def make_llm_request():
    # Ваш код
    return result
```

## Боты Telegram

Хорошей практикой является отслеживания всех хендлеров.

Применяйется на хендлеры и обработки callback кнопок декоратор или контекстный менеджеры action_tracking и action_tracking_decorator
В качестве имени указывайте суффикс "_handler" action_tracking(name="menu_handler"), это позволит офильтровать на 
графике только метрики для хэндлеров

## Именование отслеживаемых action

Для обработчиков Telegram, суффикс "_handler"
Для регулярных задач, суффикс "_task"
Для вызовов llm, суффикс "_llm_call"
Для запуска агента llm, суффикс "_agent"

Разделитель для имен: "_"

## 📖 API Документация

#### action_tracking(name: str)
Контекст-менеджер для отслеживания действий:
- Автоматически измеряет время выполнения
- Подсчитывает успешные и ошибочные выполнения
- Позволяет трекить размер обработанных данных

#### action_tracking_decorator(name: str)
Декоратор для функций и корутин, поддерживает все возможности `action_tracking`.

## 🔍 Метрики и мониторинг

### Доступные метрики

Все метрики имеют префикс `genapp_`:

#### HTTP метрики:
- `genapp_http_requests_total` - Общее количество HTTP запросов
- `genapp_http_request_duration_sec` - Гистограмма времени выполнения
- `genapp_http_request_size_bytes` - Размер запросов/ответов

#### Метрики действий:
- `genapp_action_count_total` - Количество выполненных действий
- `genapp_action_duration_sec` - Время выполнения действий
- `genapp_action_size_total` - Размер обработанных данных

### Labels (теги)

Метрики содержат labels:
- http_requests_total → method, status, resource, app_type, env, app
- http_request_duration_sec → method, status, resource, app_type, env, app
- http_request_size_bytes → resource, status, method, direction, app_type, env, app
- action_count_total → name, status, env, app
- action_duration_sec → name, env, app
- action_size_total → name, env, app

---

Про утилиты
- Минималистичный конечный автомат [fsm.py](../../project/libs/fsm.py) (машина состояний, FSM).
  TODO: Добавить примеры использования

TODO: описать другие утилиты

---

# Про библиотеки

## Alembic
- Alembic для создания миграций базы данных

## uvloop
Асинхронные приожения запускаются через uvloop.
Он гораздо быстрее.

## Линтеры
про них написано в [linters.md](linters.md)

## python-telegram-bot
Используется для создания ботов

## FastAPI
Используется для создания API

TODO: добавить про другие библиотеки

---

# Правила использования переменных окружения через project.settings.Settings

TODO: рассказать про SecretStr

## Правильное использование Settings

Объект `Settings` в файле `project/settings.py` реализован через `LazyInit`
и должен использоваться **только** через вызов класса `Settings().param_name`.

Это обеспечивает правильную работу ленивой инициализации, потокобезопасность и
возможность динамического переопределения настроек для тестирования.

### 1. Ленивая инициализация
`LazyInit` создает экземпляр настроек только при первом обращении
и переиспользует его в рамках одного контекста выполнения. Это обеспечивает:
- Отложенную загрузку конфигурации!
- Экономию памяти
- Переопределять настройки для тестов через `Settings.local(**kwargs)`

## ❌ АНТИПАТТЕРНЫ - что НЕ надо делать

### 1. Создание локальных переменных
```python
# ❌ НЕПРАВИЛЬНО
settings = Settings()
model_name = settings.LLM_MODEL_NAME
```

**Почему плохо:**
- Нарушает паттерн ленивой инициализации!
- Создает ненужную ссылку на объект
- Может привести к использованию устаревшего экземпляра при изменении контекста
- Усложняет тестирование с переопределением настроек

### 2. Использование в аргументах функций
```python
# ❌ НЕПРАВИЛЬНО
def process_data(settings=Settings()):
    return settings.MAX_TOKENS

# ❌ НЕПРАВИЛЬНО
def create_agent(config: SettingsValidator = Settings()):
    pass
```

**Почему плохо:**
- Создает экземпляр на момент определения функции, а не вызова
- Нарушает принцип единственного источника истины
- Делает функцию менее тестируемой
- Может привести к использованию устаревших настроек

### 3. Сохранение в атрибутах класса
```python
# ❌ НЕПРАВИЛЬНО
class MyClass:
    def __init__(self):
        self.settings = Settings()  # ❌ ПЛОХО

    def process(self):
        return self.settings.MAX_TOKENS
```

**Почему плохо:**
- Фиксирует экземпляр настроек на момент создания объекта!
- Препятствует динамическому изменению настроек
- Усложняет тестирование с мокированием настроек

## Тестирование с переопределением настроек

```python
# ✅ ПРАВИЛЬНО для тестов
def some_function():
    print(Settings().MAX_TOKENS)

with Settings.local(MAX_TOKENS=1000, TEMPERATURE=0.5):
    result = some_function()
    # В этом контексте some_function и Settings().MAX_TOKENS вернет 1000
```

---

Создавайте обработчики телеграма в таком виде.

Не нужно подавлять ошибки внутри обработчика, потому что декоратор processing_errors должен его 
перехватить и он является предпочтительным местом обработчик ошибок, являясь централизованным местом обработки ошибок, 
чтоб избежать дублирования кода по обработке ошибок в каждом обработчике.

{Объяснить каждый декоратор для телеграмма из project/infrastructure/utils/telegram.py}

Порядок декораторов важен!

```python
@check_auth
@timeout_with_retry
@processing_errors
@action_tracking_decorator("start_handler")
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = f"Привет {user_id}! Это пример обработчика Телеграм!"

    await update.message.reply_text(message)
```
