Файл генерируется автоматически из файлов в specs/rules/*

---

- [📖 Какую спецификацию читать для вашего сценария](#-какую-спецификацию-читать-для-вашего-сценария)
- [📥 Установка](#-установка)
- [🚀 Запуск](#-запуск)
- [🧪 Тестирование](#-тестирование)
- [💻 Разработка](#-разработка)
- [📂 Структура проекта](#-структура-проекта)
- [📚 Документация](#-документация)

# Архитектурный шаблон для сервисов GEN AI

Шаблон составлен с учетом опыта разработки сервисов в GEN AI.
Разработчики прошли через ~~боль и слезы~~ плохие решения, ошибки, оверинжиниринг и неудобный дизайн.
Чтоб не делать одни и те же ошибки, мы собрали оптимальные решения в этом проекте.

- 🔧 В этом проекте заложены необходимые инфраструктурные настройки для развертывания и работы сервиса внутри контура
- 🤖 Запуск Telegram бота с мониторингом HTTP запросов в Prometheus и необходимыми инфрастурктурными настройками контура
- ⚡ Запуск FastAPI с мониторингом HTTP запросов в Prometheus и необходимыми инфрастурктурными настройками контура
- 📐 Определена структура моделуй и их границы (что должно и не должно в них находится)
- 🔌 Готовые интеграции с нашими сервисами внутри контура с отслеживанием запросов через Prometheus (Клиенты-адаптеры для 
  баз данных, аутентификации, llm моделей, OpenAI, keycloak и другие)
- 🛠️ Набор переиспользуемых утилит, декораторов и другого шаблонного кода
- 📝 Правильно настроенное логирование и получение переменных окружений с валидацией
- 🐳 Докер контейнер для быстрого локального развертывания с инфраструктурой
- ✅ Все необходимое для создания автотестов без боли
- 📚 Набор проверенных библиотек, с которыми мы работаем
- 🎨 Вайбкодинг с файлом AGENTS.md с подробными правилами и инструкциями для генерации кода через LLM агента

✨ **Преимущества шаблона:**
- 🎯 Позволит вам сосредоточиться на бизнес-логике
- 🔄 Стандартизирует повторяемый код в разных проектах 
- 🚀 Разработчики будут быстрее развертывать проекты в контуре

## 📖 Какую спецификацию читать для вашего сценария

В директории `specs/rules/` находятся спецификации с подробными правилами и рекомендациями по разработке:

**✨ Создание нового функционала:**
- 🔌 Создать адаптер к внешнему API → [create-adapter.md](specs/rules/create-adapter.md)
- 🤖 Создать обработчик Telegram бота → [telegram-handlers.md](specs/rules/telegram-handlers.md)
- 🌐 Создать API эндпоинт → [fastapi-and-api-endpoints.md](specs/rules/fastapi-and-api-endpoints.md)
- 🗄️ Добавить миграцию БД → [alembic-db-migration.md](specs/rules/alembic-db-migration.md)
- 🧪 Создать авто-тест → [auto-tests.md](specs/rules/auto-tests.md)
- 🚨 Как создать своё исключение → [exceptions.md](specs/rules/exceptions.md)
- Как создать ORM модель → [create-orm-model.md](specs/rules/create-orm-model.md)
- 🎨 Вайбкодинг → [development.md](specs/rules/development.md)

**🏛️ Работа с архитектурой:**
- 📐 Понять структуру слоев и границы модулей → [layers.md](specs/rules/layers.md)
- Доменно-специфичные типы → [tiny-types.md](specs/rules/tiny-types.md)
- 🔌 Узнать про существующие адаптеры → [adapters.md](specs/rules/adapters.md)
- ⚠️ Как избежать типичных ошибок и сохранить нервы и время, себе и другим → [anti-patterns.md](specs/rules/anti-patterns.md)
- 🧱 Какие есть переиспользуемые модули в проекте → [project-utils.md](specs/rules/project-utils.md)

**⚙️ Инфраструктура и конфигурация:**
- 🗄️ Как работать с бд через ORM, сессии и транзакции → [database-sessions.md](specs/rules/database-sessions.md)
- 🔧 Как добавить переменные окружуния и использовать их в проекте → [settings-and-environments.md](specs/rules/settings-and-environments.md)
- 📊 Настроить мониторинг для функции или участка кода → [monitoring.md](specs/rules/monitoring.md)
- ⏱️ Использовать ленивую инициализацию → [lazy-init-objects.md](specs/rules/lazy-init-objects.md)
- 🔍 Настроить линтеры → [linters.md](specs/rules/linters.md)
- 📦 Выбор и использование внешних библиотек → [python-libs.md](specs/rules/python-libs.md)

## 📥 Установка
Мы используем пакетный менеджер UV,
[как установить](https://docs.astral.sh/uv/getting-started/installation/#installation-methods).

### Основные зависимости

```bash
# Установка всех зависимостей
uv sync --all-groups
```

### Группы зависимостей

Зависимости организованы по группам для более гибкой установки:

**`dev`** - зависимости для разработки
```bash
uv sync --locked --group dev
# или вместе с основными
uv sync --locked --all-extras
```

**`voice`** - обработка аудио (голос)
```bash
uv sync --locked --group voice
```

**`telegram`** - Telegram бот + uvloop + Flask
```bash
uv sync --locked --group telegram
```

**`restapi`** - FastAPI + uvicorn
```bash
uv sync --locked --group restapi
```

**`database`** - Alembic + PostgreSQL + SQLAlchemy
```bash
uv sync --locked --group database
```

Либо через pip
```bash
pip install -r requirements.txt -r requirements.dev.txt
```

### Переменные окружения

Нужно создать файл с переменными окружения `.env` в директории,
пример файла с обязательными переменнами в [env.example](env.example).
Ознакомьтесь с переменными окружения в [settings.py](project/settings.py).

Linux
```bash
cp .env.example .env
```
Windows
```powershell
Copy-Item .env.example .env
```
Crossplatform
```bash
python3 -c "import shutil; shutil.copy('.env.example', '.env2')"
```

## 🚀 Запуск

Запускайте приложение с переменной окружения `ENV=LOCAL`, оно выключает проверку аутентификации и другие вещи, которые
не нужны в локальной раработке.

**⚡ Fastapi**
```bash
uv run uvicorn project.infrastructure.apps.api:app
```

**🤖 Telegram Bot**
```bash
uv run python -m project.infrastructure.apps.bot
```

Для продакшена написать запуск в модуле [main.py](project/infrastructure/apps/main.py)
и запустить таким образом:
```bash
python -m project.infrastructure.apps.main
```

TODO: как запустить через докер

## 🧪 Тестирование

Для запуска тестов используйте:
```bash
pytest --cov=project tests/
```

Уровень логирование в тестах настраивается в [pytest.ini](pytest.ini)

## 💻 Разработка

Следуйте [соглашению](https://www.conventionalcommits.org/en/v1.0.0/) именования комитов.

Форматирование кода и линтеры выполняется автоматически при коммите через pre-commit хуки.
Чтобы активировать pre-commit, выполните:
```bash
pre-commit install
```

Настройки линтеров находятся в [pyproject.toml](pyproject.toml).
Настройки линтеров для тестов находятся в [ruff-tests.toml](tests/ruff-tests.toml).

При коммите автоматически выполняются:
- ✅ ruff check --fix (линтер)
- 🎨 ruff format (форматирование кода)
- 💉 di-linter (проверка инъекций зависимостей)
- 🏛️ la-linter (проверка архитектурных слоев)
- 📦 обновление requirements.txt через UV

## 📂 Структура проекта

Модули объединяются по компонентам, так рекомендуются в чистой архитектуре, в DDD, это наиболее оптимально.
Благодаря этому взглянув на структуру проекта, можно сразу понять, про что он.
И не надо прыгать по директориям, искать модули относящиеся к одному компоненту.

Границы модулей:
- `project/infrastructure/apps/bot.py` - Telegram bot
- `project/infrastructure/apps/flask.py` - Запускатеся на проде для параллельного запуска с Telegram bot для 
  создания эндпоинтов health-check и prometheus
- `project/infrastructure/apps/api.py` - FastAPI app
- `project/infrastructure/apps/main.py` - Запуск приложения на проде, там их может быть несколько запущено параллельно, 
  поэтому отдельный модуль
- `project/infrastructure/adapters/*` - интеграции к внешним системам (адаптеры, клиенты)
- `project/infrastructure/utils` - универсальный переиспользуемые код, не связанный с бизнес-логикой, относящиеся к
- `project/components/{component}/cli.py` - обработчики CLI интерфейса
- `project/components/{component}/endpoints.py` - эндпоинты API
- `project/components/{component}/handlers.py` - обработчики бота
- `project/components/{component}/models.py` - модели данных ORM
- `project/components/{component}/repositories.py` - Любое обращение к данным
- `project/components/{component}/enums.py` - Наборы значений
- `project/components/{component}/usecases.py` - точка входа в бизнес-логику (сценарии использования приложения)
- `project/components/{component}/service.py` - детали реализации бизнес-логики (когда бизнес-логика не влезает в  
  usecases.py, переноси сюда)
- `project/components/{component}/exceptions` - исключения бизнес-логики относящиеся к компоненту
- `project/components/{component}/schemas.py` - схемы данных и/или валидация pydantic
- `project/components/{component}/ai/{agent_name}/exceptions.py`
- `project/components/{component}/ai/{agent_name}/schemas.py` - схемы данных агента (pydantic модели)
- `project/components/{component}/ai/{agent_name}/prompts.py` - llm промпты, еще второй вариант ниже, где каждый промпт 
  в отдельнос файле, в общей директории prompts
- `project/components/{component}/ai/{agent_name}/prompts/*.py` - llm промпты
- `project/components/{component}/ai/{agent_name}/tools/*.py` - инструменты ai агента
- `project/components/{component}/ai/{agent_name}/agent.py` - логика ai агента
- `project/libs/*` - универсальный переиспользуемые код, не связанный с бизнес-логикой и инфраструктурой
- `project/exceptions.py` - базовые исключения
- `project/logger.py` - настройки логирования
- `project/settings.py` - Переменные окружения
- `project/container.py` - Контейнер для внедрения зависимостей
  фреймворками. Почему не в `project/libs`? Потому что там запрещен импорт из project.infrastructure.
- `tests/test_*` - Автотесты
- `tests/conftest.py` - Фикстуры
- `tests/factories.py` - Фабрики данных
- `alembic/versions/*` - Миграции бд
- `scripts/*` - Скрипты
- `specs/rules/*` - Документация и спецификации по разработке используя этот шаблон и заложенный в нем стиль
- `specs/features/*` - Спецификация по разработке фичи при вайбкодинге

## Вайбкодинг

Для того, чтобы работать с внешними моделями, 
можно сгенерировать промпт с содержимом модулей проекта, через команду:
```bash
uv run python ./scripts/project_prompt.py # по умолчанию конфиг ./project-prompt.toml
uv run python ./scripts/project_prompt.py -c my-custom-config.toml
```
Управлять тем, какие файлы войдут в промпт, можно через конфиг [project-prompt.toml](project-prompt.toml)

- Если модель не соблюдает правила игры, пропускает и не соблюдает какие то требования, то нужно добавить инструкции 
  или исправить существующие в ./specs/rules
- Добавляйте в контекст модели весь файл [AGENTS.md](./AGENTS.md), он формируется автоматически из всех файлов в
  ./specs/rules

## 📚 Документация

В директории `specs/rules/` находятся документация по использованию шаблона:

- [adapters.md](specs/rules/adapters.md) - Общие принципы работы с адаптерами и обзор существующих адаптеров
- [alembic-db-migration.md](specs/rules/alembic-db-migration.md) - Создание и управление миграциями базы данных через Alembic
- [anti-patterns.md](specs/rules/anti-patterns.md) - Антипаттерны, которых следует избегать в разработке
- [database-sessions.md](specs/rules/database-sessions.md) - Управление сессиями и транзакциями базы данных (asession, atransaction, current_atransaction)
- [auto-tests.md](specs/rules/auto-tests.md) - Правила написания и запуска автотестов
- [create-adapter.md](specs/rules/create-adapter.md) - Пошаговая инструкция по созданию адаптера к внешней системе
- [exceptions.md](specs/rules/exceptions.md) - Правила работы с исключениями и создание собственных ошибок
- [fastapi-and-api-endpoints.md](specs/rules/fastapi-and-api-endpoints.md) - Best practices для создания API эндпоинтов
- [layers.md](specs/rules/layers.md) - Архитектурные границы и слои приложения
- [lazy-init-objects.md](specs/rules/lazy-init-objects.md) - Ленивая инициализация объектов вместо глобальных переменных
- [linters.md](specs/rules/linters.md) - Запуск линтеров и инструментов проверки кода
- [monitoring.md](specs/rules/monitoring.md) - Настройка мониторинга через Prometheus
- [project-utils.md](specs/rules/project-utils.md) - Описание переиспользуемых утилит
- [python-libs.md](specs/rules/python-libs.md) - Рекомендации по использованию библиотек Python
- [settings-and-environments.md](specs/rules/settings-and-environments.md) - Работа с переменными окружения через Settings
- [development.md](specs/rules/development.md) - Методология разработки на основе спецификаций
- [telegram-handlers.md](specs/rules/telegram-handlers.md) - Правила создания обработчиков Telegram бота
- [create-orm-model.md](specs/rules/create-orm-model.md) - Правила создания ORM моделей
- [tiny-types.md](specs/rules/tiny-types.md) - Доменно-специфичные типы


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
Пример использования в [test_use_case.py](../../tests/test_domains/test_chat/test_use_case.py).

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
- Устанавливает тестовое окружение (ENV="AUTOTESTS", токены, ключи)
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

**`httpx_responses`**
- Для мокирования синхронных HTTP запросов (httpx)
- Использует библиотеку respx

Пример использования:
```python
def test_external_api(httpx_responses):
    httpx_responses.add(
        "GET",
        "https://api.example.com/data",
        json={"result": "success"},
        status=200
    )
    # Теперь запросы на этот URL вернут mock-ответ
```

**`aiohttp_responses`**
- Для мокирования асинхронных HTTP запросов (aiohttp)
- Использует библиотеку aioresponses

Пример использования:
```python
async def test_external_api_async(aiohttp_responses):
    aiohttp_responses.add(
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

# Обработка дисконнектов клиентов в FastAPI

При работе с LLM и стриминговыми ответами важно корректно обрабатывать ситуации,
когда клиент неожиданно закрывает соединение. Без обработки дисконнектов:
- GPU продолжает генерацию токенов впустую
- Транзакции в БД могут остаться незавершёнными
- Ресурсы сервера тратятся впустую

## Расположение

`project/infrastructure/utils/disconnect.py`

## Основные концепции

### Как работает обнаружение дисконнекта

ASGI-сервер (Uvicorn) отправляет событие `http.disconnect` при закрытии соединения.
Для обнаружения нужно явно опрашивать `await request.receive()` и проверять тип сообщения.

**Важно:** Не используйте `request.is_disconnected()` — он некорректно работает с `BaseHTTPMiddleware`.

## Автоматическая обработка через Middleware (рекомендуется)

Добавьте `DisconnectMiddleware` в приложение — он автоматически обрабатывает дисконнекты для обычных эндпоинтов.

```python
from fastapi import FastAPI
from project.infrastructure.utils.disconnect import DisconnectMiddleware

app = FastAPI()
app.add_middleware(DisconnectMiddleware)
```

**Примечание:** Для стриминговых эндпоинтов (StreamingResponse, EventSourceResponse) middleware пропускает обработку, так как они имеют встроенную логику отмены. Для стриминга используйте `detect_disconnect()` или полагайтесь на `sse-starlette`.

## Утилиты для ручной обработки

### 1. Декоратор `@with_cancellation`

Для обычных (не-стриминговых) эндпоинтов — автоматически отменяет обработчик при дисконнекте.

```python
from project.infrastructure.utils.disconnect import with_cancellation
from fastapi import Request

@app.post("/process")
@with_cancellation
async def process_job(job: JobRequest, raw_request: Request):
    try:
        result = await llm.generate(job.prompt)
        return {"result": result}
    except asyncio.CancelledError:
        # Логируем отмену, отправляем метрики
        raise  # Пробрасываем исключение дальше
    finally:
        # Очистка ресурсов с защитой от отмены
        with shield_cancel_scope():
            await cleanup()
```

### 2. Контекстный менеджер `detect_disconnect`

Для гранулярного контроля — защищает критичные операции и позволяет отменять выборочно.

```python
from project.infrastructure.utils.disconnect import detect_disconnect, cancel_on_disconnect

@app.post("/process")
async def process_job(job: JobRequest, request: Request):
    async with detect_disconnect(request) as disconnect_event:
        # Защищено от отмены — выполнится всегда
        await db.log_request(job.job_id)

        # Проверяем, отключился ли клиент
        if disconnect_event.is_set():
            await db.log_cancellation(job.job_id)
            return Response(status_code=499)

        # Может быть отменено при дисконнекте
        result = await cancel_on_disconnect(
            expensive_operation(),
            disconnect_event
        )

        return result
```

### 3. Функция `shield_cancel_scope`

Защита критичных операций от отмены в стриминговых ответах.

```python
from project.infrastructure.utils.disconnect import shield_cancel_scope

async def stream_response():
    try:
        async with aclosing(generate_chunks()) as gen:
            async for chunk in gen:
                yield chunk
    finally:
        with shield_cancel_scope():
            await cleanup()  # Не будет прервано при отмене
```

### 4. Функция `safe_async_generator_cleanup`

Безопасная очистка асинхронных генераторов через `aclosing()`.

```python
from project.infrastructure.utils.disconnect import safe_async_generator_cleanup
from contextlib import aclosing

async def generate_llm_response():
    async with aclosing(llm_stream()) as stream:
        async for chunk in stream:
            yield chunk
        # aclosing() гарантирует немедленное освобождение ресурсов
```

## Особенности реализации

### Использование anyio.CancelScope для стриминга

При работе с `sse-starlette` и стриминговыми ответами используйте `anyio.CancelScope`
вместо `asyncio.shield()`, так как sse-starlette работает на anyio task groups.

```python
import anyio

with anyio.CancelScope(shield=True):
    await cleanup_operation()
```

### Обработка CancelledError

Всегда явно обрабатывайте `CancelledError`:
- Логируйте событие отмены
- Отправляйте метрики
- Пробрасывайте исключение дальше
- Выполняйте очистку в `finally` блоке

```python
try:
    result = await operation()
except asyncio.CancelledError:
    # Логируем метрику отмены
    metrics.increment("request_cancelled")
    raise  # Пробрасываем
```

### Избегайте двойной отмены

Не проверяйте дисконнект вручную внутри стриминговых генераторов, если уже
используете `EventSourceResponse` или `StreamingResponse` — фреймворки
уже обрабатывают отмену. Ручная проверка создаёт race condition.

## Когда что использовать

| Сценарий | Инструмент |
|----------|------------|
| Все эндпоинты автоматически | `DisconnectMiddleware` |
| Простой endpoint без стриминга (без middleware) | `@with_cancellation` |
| Нужна защита БД-операций | `detect_disconnect` |
| Стриминговый ответ (SSE) | `shield_cancel_scope` + `aclosing()` |
| Сложная логика с несколькими этапами | Комбинация инструментов |

## Ссылки

- [Статья на Habr](https://habr.com/ru/companies/tochka/articles/992134/)
- [vLLM implementation](https://github.com/vllm-project/vllm/blob/v0.13.0/vllm/entrypoints/utils.py)

---

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

---

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
```py
import datetime as dt

from sqlalchemy import func, MetaData
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    declarative_base,
)

public_schema = MetaData()
Base = declarative_base(metadata=public_schema)


class TimeMixin:
    created_at: Mapped[dt.datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())

```

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

---

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

---

- При удалении и переименовании объектов в коде, их также нужно изменять в документации находящихся в ./specs
- Не создавай обработку исключений для импортов пакетов
- Не используй пакет __future__
- Не делай импорты в `__init__.py` файлах пакетов — импортируй напрямую из модулей
- Создавай асинхронные контекстные менеджеры через декоратор `@asynccontextmanager` из `contextlib`, а не через класс с `__aenter__`/`__aexit__`

---

# Exceptions
Свои собственные исключения наследуйте от `project.exceptions.AppError`

---

## API Best practices
uvicorn запускается с циклом uvloop
```bash
uvicorn project.presentation.api:app -host 0.0.0.0 --loop uvloop
```

Эндпоинты должны располагаться в `project.components.{name}.endpoints`.

### Формат ответов ресурсов API
Лучше возвращать в виде словаря.
Тогда при необходимости добавление новых данных в ответе ручки, нужно будет добавить только новое поле.
Используйте готовую схему для этого `project.components.base.schemas.ApiResponse`.
Если указать в аргументе response_model, в swagger появится документация по выводу.
Но в случае тяжелых данных это может быть затратно по времени,
потому что данные буду валидироваться через `pydantic`, это замедляет 2.5 раза по сравнению с обычным dict/dataclass.

```python
from project.components.base.schemas import ApiResponseSchema


@app.get("/my", response_model=ApiResponseSchema[list[int]])
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


## Обработка исключений в FastAPI

### Правильный подход к обработке исключений

Поток обработки ошибок: Бизнес-логика → raise Exception → FastAPI Exception Handler → HTTP Response

**В бизнес-логике** поднимать обычные исключения (наследники `AppError`):

```python
# В use cases, services, repositories
def process_user(user_id: int):
    user = user_repo.get(user_id)
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    return user
```

**В FastAPI эндпоинтах** использовать обработчики исключений FastAPI для преобразования бизнес-исключений в HTTP ответы:

```python
app = FastAPI(...)

@app.exception_handler(Exception)
async def custom_exception_handler(request, exc: Exception):
    message = f"Unexpected Error: {exc}"
    logger.exception(message)
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    message = f"{request.method} {request.url} {exc.status_code}"
    if exc.detail:
        message = f"{message} ({exc.detail})"

    if Settings().is_local():
        message = f"{message} headers={request.headers}"

    logger.error(message)

    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    message = f"{request.method} {request.url} {status.HTTP_422_UNPROCESSABLE_ENTITY} ({exc.errors()})"
    logger.error(message)
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(exceptions.NotFoundError)
async def not_found_error_handler(request: Request, exc: exceptions.NotFoundError):
    message = f"{request.method} {request.url} {status.HTTP_404_NOT_FOUND} ({exc})"
    logger.error(message)
    return ORJSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(exceptions.AuthError)
async def auth_error_handler(request: Request, exc: exceptions.NotFoundError):
    message = f"{request.method} {request.url} {status.HTTP_401_UNAUTHORIZED} ({exc})"
    logger.error(message)
    return ORJSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


@app.exception_handler(exceptions.ExternalApiError)
async def integration_error_handler(request: Request, exc: exceptions.NotFoundError):
    message = f"{request.method} {request.url} {status.HTTP_500_INTERNAL_SERVER_ERROR} ({exc})"
    logger.error(message)
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )
```

### Почему так правильно?

1. **Разделение ответственностей**: Бизнес-логика не знает о HTTP, фреймворк обрабатывает HTTP аспекты
2. **Переиспользование**: Одна бизнес-логика может использоваться в разных контекстах (API, CLI, тесты)
3. **Тестируемость**: Легче тестировать бизнес-логику без HTTP зависимостей
4. **Читаемость**: Код бизнес-логики фокусируется на логике, а не на HTTP деталях

### Антипаттерны

❌ **Не использовать HTTPException в бизнес-логике:**
```python
# ПЛОХО: бизнес-логика зависит от FastAPI
def process_user(user_id: int):
    user = user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")  # ❌
    return user
```

❌ **Не подавлять исключения в эндпоинтах:**
```python
# ПЛОХО: скрывает ошибки
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        user = await user_service.get_user(user_id)
        return user
    except Exception as e:
        return {"error": "Something went wrong"}  # ❌
```

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
Пример в [interfaces.py](project/components/chat/interfaces.py)

Из-за того, что бизнес-логика не зависит от деталей реализации, упрощается тестирование.
Пример теста бизнес-логики посмотрите тут [test_ask.py](tests/test_domains/test_chat/test_ask.py)

Пример, как надо писать модули смотрите на примере домена [chat](project/components/chat)

## Слои

Считаю, что абстракции UseCase, Service, Repository
могут быть достаточными для скрытия сложности на ранней стадии проекта.
Вводить новые сущности можно по мере увеличения сложности проекта.
Поэтому ограничимся описанием этих паттернов.

**UseCase** - точка входа в бизнес-сценарии. Пример [use_cases.py](project/components/chat/use_cases.py).
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

**Service** - скрывает детали реализации бизнес-процесса. Пример [service.py](project/components/chat/service.py)
Может объединять в себе работу одного или нескольких доменов.\
Объект без состояния.

**Repository** - нужны, чтобы отделить доступ к данным от ORM. Пример [repositories.py]
(project/components/chat/repositories.py)\
Объект без состояния.

- доступ к данным изолируйте в классах Repository, в бизнес-логике извлечение данных из бд затрудняет 
  читать и понимать саму бизнес-логику. Ищите примеры в модулях [repositories.py](project/components/user/repositories.py)
- Есть generic базовый класс с базовыми методами, наследуйте ваши Repository от него, пример в [repositories.py](project/components/user/repositories.py)

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
Пример [interfaces.py](project/components/chat/interfaces.py).
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

## Переменные окружение проекта
```py
import os
import typing as t
from enum import Enum
from pathlib import Path

from pydantic import PostgresDsn, AfterValidator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from project.libs.structures import LazyInit


def not_empty_validator(value):
    if not value:
        error_msg = "Field cannot be empty"
        raise ValueError(error_msg)
    return value


NotEmptyStrT = t.Annotated[str, AfterValidator(not_empty_validator)]
NotEmptySecretStrT = t.Annotated[SecretStr, AfterValidator(not_empty_validator)]


class Constants:
    MONITORING_APP_NAME = ""
    API_ROOT_PATH = os.getenv("API_ROOT_PATH", "/api")


class Envs(Enum):
    PROD = "PROD"  # to work at a prod stand
    LAMBDA = "LAMBDA"  # to work at a stable stand
    SANDBOX = "SANDBOX"  # to work on a test stand
    TEST = "AUTOTEST"  # for run testing
    LOCAL = "LOCAL"  # for local development


class SettingsValidator(BaseSettings):
    # Application
    ENV: Envs = Envs.PROD
    API_TOKEN: NotEmptySecretStrT
    HISTORY_WINDOW: int = 20

    # Keycloak
    KEYCLOAK_URL: str = ""
    KEYCLOAK_CLIENT_ID: str = ""
    KEYCLOAK_USERNAME: str = ""
    KEYCLOAK_PASSWORD: SecretStr | None = None

    # Auth service
    BOT_AUTH_SERVICE_URL: str = ""

    # Database
    SQLALCHEMY_DATABASE_DSN: PostgresDsn  # Example: postgresql+psycopg2://user:password@localhost:5432/database
    DATABASE_PRE_PING: t.Annotated[bool, "Checks and creates connection if closed before requesting"] = False

    # Telegram
    TELEGRAM_BOT_TOKEN: NotEmptySecretStrT
    TELEGRAM_BASE_URL: str = ""
    TELEGRAM_FILE_BASE_URL: str = ""

    # Redis
    REDIS_HOST: str = ""
    REDIS_PORT: str = ""
    REDIS_DB: str = ""

    # LLM
    LLM_MODEL: NotEmptyStrT
    LLM_API_KEY: NotEmptySecretStrT
    LLM_MIDDLE_PROXY_URL: str = ""
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 8192
    LLM_TIMEOUT: float | None = None

    # Langfuse
    LANGFUSE_TRACING_ENABLED: bool = "false"
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_HOST: str | None = None

    # Logging
    WRITE_LOGS_TO_FILE: bool = False
    LOG_LEVEL: str = "INFO"
    FASTAPI_LOG_LEVEL: str = "INFO"
    TELEGRAM_LOG_LEVEL: str = "INFO"
    HTTP_REQUESTS_LOG_LEVEL: str = "ERROR"
    SQLALCHEMY_LOG_LEVEL: str = "ERROR"
    REDIS_LOG_LEVEL: str = "ERROR"
    FLASK_LOG_LEVEL: str = "ERROR"

    # Loading local settings for development environment.
    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent / ".env", extra="allow")

    def is_local(self):
        return self.ENV == Envs.LOCAL

    def is_production(self):
        return self.ENV == Envs.PROD

    def is_testable_stand(self):
        return self.ENV in (Envs.LAMBDA, Envs.SANDBOX)

    def is_any_stand(self):
        return self.ENV in (Envs.PROD, Envs.LAMBDA, Envs.SANDBOX)


Settings = LazyInit(SettingsValidator)

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

---

# Доменно-специфичные типы.

Не используйте в аннотациях примитивные типы str, int и т.п.
Вместо этого создавайте типы для каждой сущности с именем, которое будет отражать сущность этого объекта.
Код с такими типами лучше читается, устраняет двусмысленность и устраняет риск перепутать объекты.

Пример:
```python
import typing as t

UserIdT = t.NewType("UserIdT", t.Annotated[int, "User ID"])
```

Такие типы размещаются в [datatypes.py](../../project/datatypes.py)

Список всех таких типов в проекте:
```py
import typing as t

UserIdT = t.NewType("UserIdT", t.Annotated[int, "User ID"])
ChatIdT = t.NewType("ChatIdT", t.Annotated[int, "Chat ID"])
MessageIdT = t.NewType("MessageIdT", t.Annotated[int, "Message ID"])
AnswerT = t.NewType("AnswerT", t.Annotated[str, "Ответ пользователю"])
QuestionT = t.NewType("QuestionT", t.Annotated[str, "Вопрос пользвоателя"])

```
