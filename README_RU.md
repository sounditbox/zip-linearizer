# Zip Linearizer

Утилита для линейзации содержимого ZIP-архивов в единый текстовый файл.

## Описание

Zip Linearizer - это инструмент командной строки для извлечения текстового содержимого из ZIP-архивов и объединения его в один линейный текстовый файл. Поддерживает различные форматы текстовых файлов (исходный код, конфигурации, документация и т.д.), а также **прямую работу с GitHub репозиториями и Pull Request**.

## Особенности

- ✅ Определение текстовых файлов по расширениям
- ✅ Поддержка множества форматов файлов (Python, JavaScript, HTML, CSS, Markdown и др.)
- ✅ Декодирование с поддержкой UTF-8 и fallback на latin-1
- ✅ Отчет о прогрессе обработки
- ✅ Настраиваемые разделители между файлами
- ✅ **Поддержка GitHub репозиториев** - скачивание и обработка прямо из GitHub
- ✅ **Поддержка Pull Request** - автоматическое использование ветки источника из PR
- ✅ Чистая архитектура с применением принципов SOLID
- ✅ Полное покрытие тестами
- ✅ Логирование и обработка ошибок
- ✅ Подробная статистика обработки

## Установка

### Требования

- Python 3.8 или выше
- Poetry (опционально, для управления зависимостями)

### Установка с Poetry (рекомендуется)

```bash
# Установка Poetry (если еще не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# Клонирование репозитория
git clone <repository-url>
cd zip_linealizer

# Установка зависимостей
poetry install

# Активация виртуального окружения
poetry shell
```

### Установка без Poetry

```bash
# Клонирование репозитория
git clone <repository-url>
cd zip_linealizer

# Создание виртуального окружения (рекомендуется)
python -m venv venv

# Активация виртуального окружения
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Установка пакета в режиме разработки (опционально)
pip install -e .
```

### Установка зависимостей напрямую

Если вы не хотите устанавливать пакет как модуль, можно просто установить зависимости:

```bash
pip install requests
```

И запускать скрипт напрямую:

```bash
python -m zip_linearizer.core.cli archive.zip
```

## Использование

### Базовое использование

```bash
# С Poetry
poetry run zip-linearizer sample.zip

# Без Poetry (если установлен пакет)
zip-linearizer sample.zip

# Без Poetry (запуск модуля напрямую)
python -m zip_linearizer.core.cli sample.zip
```

Это создаст файл `sample.linearized.txt` с содержимым всех текстовых файлов из архива.

### Указание выходного файла

```bash
poetry run zip-linearizer sample.zip -o output.txt
# или
python -m zip_linearizer.core.cli sample.zip -o output.txt
```

### Настройка разделителя

```bash
poetry run zip-linearizer sample.zip -d "\n=== Файл ===\n"
```

### Работа с GitHub репозиториями

Приложение поддерживает прямое скачивание и обработку GitHub репозиториев:

```bash
# Обработка репозитория (используется дефолтная ветка)
poetry run zip-linearizer https://github.com/owner/repo
# или
python -m zip_linearizer.core.cli https://github.com/owner/repo

# Обработка конкретной ветки
poetry run zip-linearizer https://github.com/owner/repo/tree/main

# Обработка Pull Request (используется ветка источника)
poetry run zip-linearizer https://github.com/owner/repo/pull/123

# Pull Request с указанием файлов
poetry run zip-linearizer https://github.com/owner/repo/pull/123/files

# С указанием выходного файла
poetry run zip-linearizer https://github.com/owner/repo -o output.txt

# Сохранение временного файла архива
poetry run zip-linearizer https://github.com/owner/repo --keep-temp
```

### Параметры командной строки

- `source` - Путь к ZIP-файлу или URL GitHub репозитория (обязательный)
- `-o, --output` - Путь к выходному файлу (по умолчанию: `<имя_zip>.linearized.txt`)
- `-d, --delimiter` - Разделитель между файлами (по умолчанию: `\n---\n`)
- `-v, --verbose` - Подробный вывод (логирование на уровне DEBUG)
- `-q, --quiet` - Тихий режим (только ошибки)
- `--keep-temp` - Не удалять временный файл после обработки GitHub репозитория

## Структура проекта

```
zip_linealizer/
├── src/
│   └── zip_linearizer/     # Основной пакет
│       ├── __init__.py
│       ├── core/               # Ядро приложения
│       │   ├── __init__.py
│       │   ├── file_processor.py      # Основная логика обработки
│       │   ├── text_file_detector.py  # Определение текстовых файлов
│       │   ├── cli.py                 # Интерфейс командной строки
│       │   ├── github_handler.py      # Работа с GitHub API
│       │   ├── validator.py           # Валидация входных данных
│       │   ├── statistics.py          # Статистика обработки
│       │   └── exceptions.py          # Кастомные исключения
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py            # Настройки приложения
│       └── utils/
│           ├── __init__.py
│           ├── decoder.py             # Декодирование содержимого
│           └── logger.py              # Логирование
├── tests/                  # Тесты
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_file_processor.py
│   ├── test_text_file_detector.py
│   ├── test_decoder.py
│   ├── test_cli.py
│   ├── test_validator.py
│   ├── test_statistics.py
│   ├── test_exceptions.py
│   └── test_github_handler.py
├── .github/
│   └── workflows/         # CI/CD workflows
│       ├── ci.yml
│       ├── format.yml
│       └── release.yml
├── pyproject.toml         # Конфигурация Poetry
├── requirements.txt        # Зависимости (для установки без Poetry)
├── README.md
└── .gitignore
```

## Архитектура

Проект разработан с применением принципов SOLID:

- **Single Responsibility Principle**: Каждый класс отвечает за одну задачу
- **Open/Closed Principle**: Легко расширяется через абстракции (TextFileDetector, ContentDecoder)
- **Liskov Substitution Principle**: Реализации абстрактных классов взаимозаменяемы
- **Interface Segregation Principle**: Протоколы разделены по функциональности
- **Dependency Inversion Principle**: Зависимости от абстракций, а не от конкретных реализаций

## Разработка

### Запуск тестов

```bash
# С Poetry
poetry run pytest

# Без Poetry
pytest
```

### Запуск тестов с покрытием

```bash
# С Poetry
poetry run pytest --cov=zip_linearizer --cov-report=html

# Без Poetry (нужно установить pytest-cov)
pytest --cov=zip_linearizer --cov-report=html
```

### Форматирование кода

```bash
# С Poetry
poetry run black src tests

# Без Poetry (нужно установить black)
black src tests
```

### Проверка линтером

```bash
# С Poetry
poetry run ruff check src tests

# Без Poetry (нужно установить ruff)
ruff check src tests
```

### Проверка типов

```bash
# С Poetry
poetry run mypy src

# Без Poetry (нужно установить mypy)
mypy src
```

## Работа с API

### GitHub API

Приложение использует GitHub API для получения информации о репозиториях и Pull Request. Для публичных репозиториев не требуется аутентификация. Для приватных репозиториев можно настроить токен через переменную окружения `GITHUB_TOKEN` (функциональность будет добавлена в будущих версиях).

**Ограничения GitHub API:**
- Публичные репозитории: без ограничений
- Анонимные запросы: 60 запросов в час
- С аутентификацией: 5000 запросов в час

## Расширение функциональности

### Добавление собственного детектора текстовых файлов

```python
from zip_linearizer.core.text_file_detector import TextFileDetector

class CustomDetector(TextFileDetector):
    def is_text_file(self, filename: str) -> bool:
        # Ваша логика определения
        pass
    
    def get_extensions(self) -> set[str]:
        return {"custom_ext"}
```

### Добавление собственного декодера

```python
from zip_linearizer.utils.decoder import ContentDecoder

class CustomDecoder(ContentDecoder):
    def decode(self, content: bytes) -> str:
        # Ваша логика декодирования
        pass
```

### Использование как библиотеки

```python
from zip_linearizer.core.file_processor import FileProcessor
from zip_linearizer.core.text_file_detector import ExtensionBasedDetector
from zip_linearizer.utils.decoder import UTF8Decoder
from zip_linearizer.config.settings import ProcessingSettings
from pathlib import Path

# Создание процессора
detector = ExtensionBasedDetector()
decoder = UTF8Decoder()
settings = ProcessingSettings(delimiter="\n---\n")

processor = FileProcessor(detector, decoder, settings)

# Обработка архива
stats = processor.process_zip(Path("archive.zip"), Path("output.txt"))
print(f"Обработано файлов: {stats.processed_files}")
print(f"Пропущено файлов: {stats.skipped_files}")
```

## Устранение неполадок

### Ошибка "Не удалось скачать архив репозитория"

- Проверьте подключение к интернету
- Убедитесь, что репозиторий существует и публичен
- Проверьте правильность URL

### Ошибка "Не удалось определить ветку для PR"

- Убедитесь, что PR существует
- Проверьте, что PR не был закрыт или удален
- Проверьте ограничения GitHub API (rate limiting)

### Ошибка "ZIP-файл не найден"

- Проверьте правильность пути к файлу
- Убедитесь, что файл существует и доступен для чтения

## Лицензия

MIT License

## Автор

Your Name

