# Changelog

Все значимые изменения в этом проекте будут документироваться в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и этот проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

## [0.2.0] - 2025-11-17

### Added
- **Claude команды**: Добавлена команда `/commit` для генерации сообщений коммитов по спецификации Conventional Commits
  - Создан файл `.claude/commands/commit.md` с правилами генерации commit messages
  - Команда анализирует git diff и генерирует сообщения в формате conventional commits

- **Claude команды**: Добавлена команда `/changelog` для генерации заполнения CHANGELOG.md
  - Создан файл `.claude/commands/changelog.md`

- **Автоматическая генерация документации**: Добавлена генерация файла `CLAUDE.md`
  - Обновлен скрипт `scripts/update_agents.py` для автоматической генерации `CLAUDE.md`
  - Файл содержит полную документацию для работы с Claude AI

- **Автоматическая генерация llms.txt**: Добавлена генерация файла `llms.txt`
  - Обновлен скрипт `scripts/update_agents.py` для автоматической генерации `llms.txt`
  - Файл содержит структурированную информацию для LLM моделей

- **Форматирование кода**: Добавлен и настроен Black для форматирования кода
  - Добавлен Black в `requirements.dev.txt`
  - Настроен Black в `pyproject.toml`
  - Обновлен `.pre-commit-config.yaml` для использования Black
  - Применено форматирование к существующим файлам:
    - `project/libs/structures.py`
    - `tests/conftest.py`
    - `tests/test_domains/test_chat/test_endpoints.py`
    - `tests/test_domains/test_chat/test_use_case.py`

### Changed
- **Документация**: Обновлены правила структуры проекта
  - Обновлен `AGENTS.md` с уточнениями по структуре проекта
  - Обновлен `README.md` с уточнениями по структуре проекта

## [0.1.0] - 2025-11-11

### Added
- Начальная версия проекта с базовой архитектурой
- Инфраструктурные настройки для развертывания
- Интеграции с внешними сервисами
- Базовые компоненты и утилиты
