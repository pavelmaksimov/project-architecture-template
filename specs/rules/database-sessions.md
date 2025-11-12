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

**Расположение:** `project/components/base/repositories.py`

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
