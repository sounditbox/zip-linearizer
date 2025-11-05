# Zip Linearizer

A utility for linearizing ZIP archive contents into a single text file.

## Description

Zip Linearizer is a command-line tool for extracting text content from ZIP archives and combining it into a single linear text file. It supports various text file formats (source code, configurations, documentation, etc.), as well as **direct work with GitHub repositories and Pull Requests**.

## Features

- ✅ Text file detection by extensions
- ✅ Support for many file formats (Python, JavaScript, HTML, CSS, Markdown, etc.)
- ✅ UTF-8 decoding with fallback to latin-1
- ✅ Processing progress reporting
- ✅ Customizable delimiters between files
- ✅ **GitHub repository support** - download and process directly from GitHub
- ✅ **Pull Request support** - automatically use source branch from PR
- ✅ Clean architecture using SOLID principles
- ✅ Full test coverage
- ✅ Logging and error handling
- ✅ Detailed processing statistics

## Installation

### Requirements

- Python 3.8 or higher
- Poetry (optional, for dependency management)

### Installation with Poetry (recommended)

```bash
git clone https://github.com/sounditbox/zip-linearizer
cd zip_linealizer
poetry install --no-root

```
And run the script directly:

```bash
python -m zip_linearizer.core.cli archive.zip
```

## Usage

### Basic usage

```bash
poetry run zip-linearizer sample.zip
```

This will create a `sample.linearized.txt` file with the contents of all text files from the archive.

### Specify output file

```bash
poetry run zip-linearizer sample.zip -o output.txt
# or
python -m zip_linearizer.core.cli sample.zip -o output.txt
```

### Configure delimiter

```bash
poetry run zip-linearizer sample.zip -d "\n=== File ===\n"
```

### Working with GitHub repositories

The application supports direct downloading and processing of GitHub repositories:

```bash
# Process repository (uses default branch)
poetry run zip-linearizer https://github.com/owner/repo
# or
python -m zip_linearizer.core.cli https://github.com/owner/repo

# Process specific branch
poetry run zip-linearizer https://github.com/owner/repo/tree/main

# Process Pull Request (uses source branch)
poetry run zip-linearizer https://github.com/owner/repo/pull/123

# Pull Request with files indication
poetry run zip-linearizer https://github.com/owner/repo/pull/123/files

# With output file specified
poetry run zip-linearizer https://github.com/owner/repo -o output.txt

# Keep temporary archive file
poetry run zip-linearizer https://github.com/owner/repo --keep-temp
```

### Command-line parameters

- `source` - Path to ZIP file or GitHub repository URL (required)
- `-o, --output` - Path to output file (default: `<zip_name>.linearized.txt`)
- `-d, --delimiter` - Delimiter between files (default: `\n---\n`)
- `-v, --verbose` - Verbose output (DEBUG level logging)
- `-q, --quiet` - Quiet mode (errors only)
- `--keep-temp` - Do not delete temporary file after processing GitHub repository

## Project Structure

```
zip_linealizer/
├── src/
│   └── zip_linearizer/     # Main package
│       ├── __init__.py
│       ├── core/               # Application core
│       │   ├── __init__.py
│       │   ├── file_processor.py      # Main processing logic
│       │   ├── text_file_detector.py  # Text file detection
│       │   ├── cli.py                 # Command-line interface
│       │   ├── github_handler.py      # GitHub API integration
│       │   ├── validator.py           # Input validation
│       │   ├── statistics.py          # Processing statistics
│       │   └── exceptions.py          # Custom exceptions
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py            # Application settings
│       └── utils/
│           ├── __init__.py
│           ├── decoder.py             # Content decoding
│           └── logger.py              # Logging
├── tests/                  # Tests
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
├── pyproject.toml         # Poetry configuration
├── requirements.txt        # Dependencies (for installation without Poetry)
├── README.md
└── .gitignore
```

## Architecture

The project is developed using SOLID principles:

- **Single Responsibility Principle**: Each class is responsible for one task
- **Open/Closed Principle**: Easily extensible through abstractions (TextFileDetector, ContentDecoder)
- **Liskov Substitution Principle**: Abstract class implementations are interchangeable
- **Interface Segregation Principle**: Protocols are separated by functionality
- **Dependency Inversion Principle**: Dependencies on abstractions, not concrete implementations

## Development

### Running tests

```bash
# With Poetry
poetry run pytest

# Without Poetry
pytest
```

### Running tests with coverage

```bash
# With Poetry
poetry run pytest --cov=zip_linearizer --cov-report=html

# Without Poetry (need to install pytest-cov)
pytest --cov=zip_linearizer --cov-report=html
```

### Code formatting

```bash
# With Poetry
poetry run black src tests

# Without Poetry (need to install black)
black src tests
```

### Linting

```bash
# With Poetry
poetry run ruff check src tests

# Without Poetry (need to install ruff)
ruff check src tests
```

### Type checking

```bash
# With Poetry
poetry run mypy src

# Without Poetry (need to install mypy)
mypy src
```

## API Usage

### GitHub API

The application uses GitHub API to get information about repositories and Pull Requests. No authentication is required for public repositories. For private repositories, you can configure a token via the `GITHUB_TOKEN` environment variable (functionality will be added in future versions).

**GitHub API limits:**
- Public repositories: no limits
- Anonymous requests: 60 requests per hour
- With authentication: 5000 requests per hour

## Extending Functionality

### Adding custom text file detector

```python
from zip_linearizer.core.text_file_detector import TextFileDetector

class CustomDetector(TextFileDetector):
    def is_text_file(self, filename: str) -> bool:
        # Your detection logic
        pass
    
    def get_extensions(self) -> set[str]:
        return {"custom_ext"}
```

### Adding custom decoder

```python
from zip_linearizer.utils.decoder import ContentDecoder

class CustomDecoder(ContentDecoder):
    def decode(self, content: bytes) -> str:
        # Your decoding logic
        pass
```

### Using as a library

```python
from zip_linearizer.core.file_processor import FileProcessor
from zip_linearizer.core.text_file_detector import ExtensionBasedDetector
from zip_linearizer.utils.decoder import UTF8Decoder
from zip_linearizer.config.settings import ProcessingSettings
from pathlib import Path

# Create processor
detector = ExtensionBasedDetector()
decoder = UTF8Decoder()
settings = ProcessingSettings(delimiter="\n---\n")

processor = FileProcessor(detector, decoder, settings)

# Process archive
stats = processor.process_zip(Path("archive.zip"), Path("output.txt"))
print(f"Processed files: {stats.processed_files}")
print(f"Skipped files: {stats.skipped_files}")
```

## Troubleshooting

### Error "Failed to download repository archive"

- Check internet connection
- Ensure repository exists and is public
- Verify URL is correct

### Error "Failed to determine branch for PR"

- Ensure PR exists
- Check that PR has not been closed or deleted
- Check GitHub API limits (rate limiting)

### Error "ZIP file not found"

- Check file path is correct
- Ensure file exists and is readable

## License

MIT License

## Author

Your Name
