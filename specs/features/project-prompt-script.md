Задача создать скрипт в ./scripts/project_prompt.py.
Скрипт будет собирать промпт из файлов в ./project 
в один файл markdown в ./project-prompt-20250101-010101.md
Нужна возможность отфильтровать модули через конфиг фильтрации в toml файле.
В скрипте нужна опция для указания пути к конфигу -c и --config.
Возможность фильтрации через паттерны fnmatch.
Полный игнор бинарных файлов.


```toml
include-paths = [
    "project/*",
    "llms.txt",
    "README.md",
    "pyproject.md",
]
exclude_paths = [
    "*cache*",
    "project/logger.py",
    "project/libs/*",
    "*.png",
    "*.jpeg",
]
exclude-empty-files = true
```

Порядок сбора модулей, сначала отрабатывает include-paths, потом исключаются exclude_paths и exclude-empty-files

Формат файла результата скрипта:
"""
# Project Prompt
build time 2025-01-01 01:01:01

## project/path/to/module.py
```python
<content>
```
## README.md
```markdown
<content>
```
"""
После создания файла печатать куда сохранился файл, на основе какого конфига был сгенерирован,
Сколько символов в файле и кол-во строк.
Тесты не нужны.