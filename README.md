# Архитектурный шаблон для сервисов GEN AI

Шаблон составлен с учетом опыта разработки сервисов в GEN AI.
Разработчики прошли через ~~боль и слезы~~ плохие решения, ошибки, оверинжиниринг и неудобный дизайн.
Чтоб не делать одни и те же ошибки, мы собрали оптимальные решения в этом проекте.

- В этом проекте заложены необходимые инфраструктурные настройки для развертывания и работы сервиса внутри контура
- Запуск Telegram бота с мониторингом HTTP запросов в Prometheus и необходимыми инфрастурктурными настройками контура
- Запуск FastAPI с мониторингом HTTP запросов в Prometheus и необходимыми инфрастурктурными настройками контура
- Определена структура моделуй и их границы (что должно и не должно в них находится)
- Готовые интеграции с нашими сервисами внутри контура с отслеживанием запросов через Prometheus (Клиенты-адаптеры для 
  баз данных, аутентификации, llm моделей, OpenAI, keycloak и другие)
- Набор переиспользуемых утилит, декораторов и другого шаблонного кода
- Правильно настроенное логирование и получение переменных окружений с валидацией
- Докер контейнер для быстрого локального развертывания с инфраструктурой
- Все необходимое для качественного создания автотестов
- Набор проверенных библиотек, с которыми мы работаем
- Вайбкодинг с файлом AGENTS.md с подробными правилами и инструкциями для генерации кода через LLM агента

Преимущества шаблона:
- Позволит вам сосредоточиться на бизнес-логике
- Стандартизирует повторяемый код в разных проектах 
- Разработчики будут быстрее развертывать проекты в контуре

## Спецификации (Specifications)

- [adapters.md](specs/rules/adapters.md) - Общие принципы работы с адаптерами и обзор существующих адаптеров
- [alembic-db-migration.md](specs/rules/alembic-db-migration.md) - Создание и управление миграциями базы данных через Alembic
- [anti-patterns.md](specs/rules/anti-patterns.md) - Антипаттерны, которых следует избегать в разработке
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
- [spec-driven-development.md](specs/rules/spec-driven-development.md) - Методология разработки на основе спецификаций
- [telegram-handlers.md](specs/rules/telegram-handlers.md) - Правила создания обработчиков Telegram бота

### Какую спецификацию читать для вашего сценария

В директории `specs/rules/` находятся спецификации с подробными правилами и рекомендациями по разработке:

**Создание нового функционала:**
- Создать адаптер к внешнему API → [create-adapter.md](specs/rules/create-adapter.md)
- Создать обработчик Telegram бота → [telegram-handlers.md](specs/rules/telegram-handlers.md)
- Создать API эндпоинт → [fastapi-and-api-endpoints.md](specs/rules/fastapi-and-api-endpoints.md)
- Добавить миграцию БД → [alembic-db-migration.md](specs/rules/alembic-db-migration.md)

**Работа с архитектурой:**
- Понять структуру слоев и границы модулей → [layers.md](specs/rules/layers.md)
- Узнать про существующие адаптеры → [adapters.md](specs/rules/adapters.md)

**Качество кода:**
- Написать тесты → [auto-tests.md](specs/rules/auto-tests.md)
- Настроить линтеры → [linters.md](specs/rules/linters.md)
- Избежать типичных ошибок → [anti-patterns.md](specs/rules/anti-patterns.md)

**Инфраструктура и конфигурация:**
- Работать с настройками → [settings-and-environments.md](specs/rules/settings-and-environments.md)
- Настроить мониторинг → [monitoring.md](specs/rules/monitoring.md)
- Использовать ленивую инициализацию → [lazy-init-objects.md](specs/rules/lazy-init-objects.md)

**Общие принципы:**
- Работа с исключениями → [exceptions.md](specs/rules/exceptions.md)
- Выбор и использование библиотек → [python-libs.md](specs/rules/python-libs.md)
- Переиспользуемые модули → [project-utils.md](specs/rules/project-utils.md)
- Разработка через спецификации → [spec-driven-development.md](specs/rules/spec-driven-development.md)


## Установка
Мы используем пакетный менеджер UV, 
[как установить](https://docs.astral.sh/uv/getting-started/installation/#installation-methods).


```bash
uv sync --locked --all-extras
```

Либо через pip
```bash
pip install -r requirements.txt
```

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

## Запуск

Запускайте приложение с переменной окружения `ENV=LOCAL`, оно выключает проверку аутентификации и другие вещи, которые
не нужны в локальной раработке.

Fastapi
```bash
uv run uvicorn project.infrastructure.apps.api:app
```

Telegram Bot
```bash
uv run python -m project.infrastructure.apps.bot
```

Для продакшена написать запуск в модуле [main.py](project/infrastructure/apps/main.py)
и запустить таким образом:
```bash
python -m project.infrastructure.apps.main
```

TODO: как запустить через докер

## Тестирование

Для запуска тестов используйте:
```bash
pytest --cov=project tests/
```

Уровень логирование в тестах настраивается в [pytest.ini](pytest.ini)

## Разработка

Следуйте [соглашению](https://www.conventionalcommits.org/en/v1.0.0/) именования комитов.

Форматирование кода и линтеры выполняется автоматически при коммите через pre-commit хуки.
Чтобы активировать pre-commit, выполните:
```bash
pre-commit install
```

Настройки линтеров находятся в [pyproject.toml](pyproject.toml).
Настройки линтеров для тестов находятся в [ruff-tests.toml](tests/ruff-tests.toml).

При коммите автоматически выполняются:
- ruff check --fix (линтер)
- ruff format (форматирование кода)
- di-linter (проверка инъекций зависимостей)
- la-linter (проверка архитектурных слоев)
- обновление requirements.txt через UV

## Структура проекта

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
- `project/domains/{component}/cli.py` - обработчики CLI интерфейса
- `project/domains/{component}/endpoints.py` - эндпоинты API
- `project/domains/{component}/handlers.py` - обработчики бота
- `project/domains/{component}/models.py` - модели данных ORM
- `project/domains/{component}/repositories.py` - Любое обращение к данным
- `project/domains/{component}/enums.py` - Наборы значений
- `project/domains/{component}/usecases.py` - точка входа в бизнес-логику (сценарии использования приложения)
- `project/domains/{component}/service.py` - детали реализации бизнес-логики (когда бизнес-логика не влезает в  
  usecases.py, переноси сюда)
- `project/domains/{component}/exceptions` - исключения бизнес-логики относящиеся к компоненту
- `project/domains/{component}/schemas.py` - схемы данных и/или валидация pydantic
- `project/domains/{component}/ai/{agent_name}/exceptions.py`
- `project/domains/{component}/ai/{agent_name}/schemas.py` - pydantic модели
- `project/domains/{component}/ai/{agent_name}/prompts.py` - llm промпты
- `project/domains/{component}/ai/{agent_name}/main.py` - логика ai агента
- `project/libs/*` - универсальный переиспользуемые код, не связанный с бизнес-логикой и инфраструктурой
- `project/exceptions.py` - базовые исключения
- `project/logger.py` - настройки логирования
- `project/settings.py` - Переменные окружения
- `project/container.py` - Контейнер для внедрения зависимостей
  фреймворками. Почему не в `project/libs`? Потому что там запрещен импорт из project.infrastructure.

## Документация

В директории `specs/rules/` находятся документация по использованию шаблона:

- [adapters.md](specs/rules/adapters.md) - Общие принципы работы с адаптерами и обзор существующих адаптеров
- [alembic-db-migration.md](specs/rules/alembic-db-migration.md) - Создание и управление миграциями базы данных через Alembic
- [anti-patterns.md](specs/rules/anti-patterns.md) - Антипаттерны, которых следует избегать в разработке
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
- [spec-driven-development.md](specs/rules/spec-driven-development.md) - Методология разработки на основе спецификаций
- [telegram-handlers.md](specs/rules/telegram-handlers.md) - Правила создания обработчиков Telegram бота
