# Создание CacheRepository

CacheRepository — это базовый класс для работы с Redis в качестве кеша. Он предоставляет унифицированный интерфейс для кеширования данных с поддержкой TTL.

Расположение: `project/components/{component}/repositories.py`

## Обязательные атрибуты класса

### key_template
Тип: `t.ClassVar[str]`

Шаблон для формирования ключей кеша. Должен содержать плейсхолдер `{}` для подстановки идентификатора:

```python
# Правильно
key_template = "user:{}"

# Неправильно
key_template = "user"  # Нет плейсхолдера
```

### ttl
Тип: `t.ClassVar[timedelta]`

Время жизни записи в кеше:

```python
# Примеры TTL
ttl = timedelta(days=7)           # 7 дней
ttl = timedelta(seconds=60)       # 60 секунд
```

## Атрибуты класса

### client
Тип: `t.ClassVar[redis_client]`

Клиент для работы с Redis. Уже определен в базовом классе:

```python
from project.infrastructure.adapters.acache import redis_client

class CacheRepository:
    client = redis_client
```

Используйте метод `cls.client()` для получения экземпляра клиента внутри методов.

## Схемы данных (Pydantic)

Для данных кеша рекомендуется использовать Pydantic схемы:

```python
from pydantic import BaseModel

class UserCacheSchema(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
```

## Правила использования

### 1. Именование класса
Имя класса должно заканчиваться на `CacheRepository` и наследоваться от `CacheRepository`:

```python
class UserCacheRepository(CacheRepository):
    ...

class ProductCacheRepository(CacheRepository):
    ...
```

### 2. Доменные типы для ключей
Используйте доменные типы из `project/datatypes.py` для аннотации ключей:

```python
from project.datatypes import UserIdT, ProductIdT

async def save(cls, user_id: UserIdT, data: "BaseModel"): ...
async def get(cls, product_id: ProductIdT): ...
```

### 3. Сериализация данных
- Используйте `orjson` для быстрой сериализации
- Используйте `data.model_dump(exclude_unset=True)` для получения словаря
- Для десериализации используйте `orjson.loads()`

Полный актуальный пример в [repositories.py](../../project/components/user/repositories.py):
```python
class UserCacheRepository(CacheRepository):
    key_template = "user:{}"
    ttl = timedelta(days=7)

    @classmethod
    async def save(cls, user_id: UserIdT, data: "BaseModel"):
        async with redis_atransaction() as tr:
            content = orjson.dumps(data.model_dump(exclude_unset=True))
            tr.set(cls.key_template.format(user_id), content, ex=cls.ttl)

    @classmethod
    async def get(cls, user_id: UserIdT):
        content = await cls.client().get(cls.key_template.format(user_id))
        if content:
            data = orjson.loads(content)
            return UserCacheSchema(**data)

        return content

    @classmethod
    async def delete(cls, user_id: UserIdT):
        async with redis_atransaction() as tr:
            tr.delete(cls.key_template.format(user_id))
```

## Дополнительные методы

При необходимости можно добавить дополнительные методы для работы с кешем:

```python
class UserCacheRepository(CacheRepository):
    ...

    @classmethod
    async def exists(cls, user_id: UserIdT) -> bool:
        """Проверка существования ключа в кеше."""
        return await cls.client().exists(cls.key_template.format(user_id)) > 0
```
