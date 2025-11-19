# Правила создания моделей данных ORM и миграций

- Таблицы в бд необходимо называть в единственном числе.
- В проекте используется sqlalchemy>=2.0 версии.
- База данных Postgres.
- После нужно создания или изменения модели нужно создать миграцию через alembic.
- При создании ORM модели нужно создавать фабрику для генерации данных этой модели в
  [factories.py](../../tests/factories.py)
- Declarative Mapping 2.0 (использование `Mapped` и `mapped_column`)
- Строгая типизация. Запрещено использовать примитивы (`int`, `str`) для идентификаторов и ключевых полей сущностей

##  1. Миксины моделей в проекте:
{include [models.py](../../project/components/base/models.py)}

## 2. Доменно-специфичные типы (Domain Types)
Для устранения двусмысленности и повышения читаемости кода, вместо примитивных типов (`int`, `str`) необходимо создавать специальные типы для каждой сущности.

- Определение: Типы создаются через `typing.NewType`, описание поля задается через `typing.Annotated`.
- Расположение: Все типы должны находиться в файле `project/datatypes.py`.

Пример (`project/datatypes.py`):
```python
import typing as t

UserIdT = t.NewType("UserIdT", t.Annotated[int, "User ID"])
OrderIdT = t.NewType("OrderIdT", t.Annotated[int, "Order ID"])
ProductNameT = t.NewType("ProductNameT", t.Annotated[str, "Product Name"])
```

## 3. Работа с Enum (Нативные типы Postgres)
В PostgreSQL следует использовать нативные ENUM типы.

1.  Python класс: Наследуйтесь от `str` и `enum.Enum`.
2.  SQLAlchemy поле: Используйте `sqlalchemy.Enum(..., name="...")`.
3.  Важно: Параметр `name` обязателен для создания типа в БД.

```python
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

# В модели:
role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role_enum"))
```

## 4. Первичные ключи (Primary Keys)
### 4.1. Типы и BigInteger
- Для аннотации типа (`Mapped[...]`) используйте доменный тип (например, `UserIdT`), а не `int`.
- Для конфигурации колонки (`mapped_column(...)`) всегда указывайте `BigInteger` (аналог `BIGSERIAL`).

```python
# Правильно:
id: Mapped[UserIdT] = mapped_column(BigInteger, primary_key=True)
```

### 4.2. Составные ключи
Если ключ составной, указывайте `primary_key=True` для каждого поля.

## 5. Реализация Many-to-Many (Через массивы)
Не создавайте промежуточные таблицы. Используйте нативный тип `ARRAY` для хранения списка идентификаторов.

- Тип колонки: `mapped_column(ARRAY(BigInteger))`.
- Аннотация: `Mapped[list[DomainIdT]]`.

```python
# Пример: Статья хранит список ID тегов
tag_ids: Mapped[list[TagIdT]] = mapped_column(ARRAY(BigInteger), default=list)
```

## 6. Индексы
- Простые: `index=True` внутри `mapped_column`.
- Составные: `Index("name", "col1", "col2")` в `__table_args__`.
- Когда добавлять: Для полей фильтрации, сортировки и внешних ключей.

## 7. Пример (Golden Sample)
Генерируй код, строго следуя этому шаблону. Обрати внимание на импорт типов из `project.datatypes`.

```python
import enum
import typing as t
from datetime import datetime

from sqlalchemy import (
    BigInteger, 
    String, 
    ForeignKey, 
    func, 
    Index, 
    Enum
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Предполагается, что этот код находится в project/datatypes.py
# Но для генерации моделей импортируй их:
# from project.datatypes import ProductIdT, ProductNameT, OrderIdT, OrderStatusT

# --- MOCK DATATYPES (для примера) ---
ProductIdT = t.NewType("ProductIdT", t.Annotated[int, "Product ID"])
ProductNameT = t.NewType("ProductNameT", t.Annotated[str, "Product Name"])
OrderIdT = t.NewType("OrderIdT", t.Annotated[int, "Order ID"])
# ------------------------------------

# 1. Base
class Base(DeclarativeBase):
    pass

# 2. Enums
class OrderStatus(str, enum.Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"

# 3. Models
class Product(Base):
    __tablename__ = "products"

    # Использование доменного типа + BigInteger
    id: Mapped[ProductIdT] = mapped_column(BigInteger, primary_key=True)
    
    # Доменный тип для строки
    name: Mapped[ProductNameT] = mapped_column(String(150), index=True)
    
    price: Mapped[int] = mapped_column(BigInteger) # Для простых значений можно int
    
    # Many-to-Many via Array of IDs
    related_product_ids: Mapped[list[ProductIdT]] = mapped_column(ARRAY(BigInteger), default=list)

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[OrderIdT] = mapped_column(BigInteger, primary_key=True)
    
    # Native Postgres Enum
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status_enum"),
        default=OrderStatus.CREATED,
        index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

class OrderLog(Base):
    __tablename__ = "order_logs"

    # Composite Primary Key Example with Domain Types
    order_id: Mapped[OrderIdT] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), 
        primary_key=True
    )
    log_index: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    message: Mapped[str] = mapped_column(String)
```

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
