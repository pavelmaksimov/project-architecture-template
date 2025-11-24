# Changelog

Все значимые изменения в этом проекте будут документироваться в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и этот проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Added
#### Генерация промптов для LLM: добавлен скрипт для генерации промптов из файлов проекта
- Создан `scripts/project_prompt.py` для автоматического создания промптов
- Добавлен конфигурационный файл `project-prompt.toml`
- Создана спецификация `specs/features/project-prompt-script.md`
- Обновлена документация `specs/rules/development.md`

#### UI для сбора файлов: добавлен интерфейс на Textual
- Создано консольное приложение `scripts/project_prompt_ui.py` - интерактивный TUI для выбора файлов для создания 
  промпта

### Changed
#### CHANGELOG: улучшено форматирование CHANGELOG.md
- Изменен промпт команды claude /changelog `.claude/commands/changelog.md`
- Обновлен CHANGELOG.md

## [0.2.0] - 2025-11-17

### Added
#### Claude команды: добавлена команда /commit для генерации сообщений коммитов
- Создан файл `.claude/commands/commit.md` с правилами генерации commit messages
- Команда анализирует git diff и генерирует сообщения в формате conventional commits

#### Система версионирования: добавлен CHANGELOG.md для проекта
- Создан файл CHANGELOG.md в соответствии со стандартом Keep a Changelog
- Создан файл claude команды `.claude/commands/changelog.md`

#### Автоматическая генерация документации: добавлена генерация файла CLAUDE.md
- Обновлен скрипт `scripts/update_agents.py` для автоматической генерации `CLAUDE.md`
- Файл содержит полную документацию для работы с Claude AI

#### Автоматическая генерация llms.txt: добавлена генерация файла llms.txt
- Обновлен скрипт `scripts/update_agents.py` для автоматической генерации `llms.txt`
- Файл содержит структурированную информацию для LLM моделей

#### Форматирование кода: добавлен и настроен Black для форматирования кода
- Добавлен Black в `requirements.dev.txt`
- Настроен Black в `pyproject.toml`
- Обновлен `.pre-commit-config.yaml` для использования Black
- Применено форматирование к существующим файлам:
  - `project/libs/structures.py`
  - `tests/conftest.py`
  - `tests/test_domains/test_chat/test_endpoints.py`
  - `tests/test_domains/test_chat/test_use_case.py`

## [0.1.0] - 2025-11-11

### Added
- Начальная версия проекта с базовой архитектурой
- Инфраструктурные настройки для развертывания
- Интеграции с внешними сервисами
- Базовые компоненты и утилиты
