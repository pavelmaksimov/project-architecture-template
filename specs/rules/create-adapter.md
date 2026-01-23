# Как добавить адаптер к внешней системе

Для создания адаптеров, работающих с внешними HTTP API, используйте классы из [base_client.py](../../project/infrastructure/utils/base_client.py).

Как замокать http запросы в тестах можно найти в спеке [auto-tests.md](auto-tests.md).

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
from project.exceptions import ExternalApiError, ServerError, ClientError


class MyServiceApiError(ExternalApiError):
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
