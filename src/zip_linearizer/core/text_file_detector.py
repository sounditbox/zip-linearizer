"""Module for detecting text files."""

from abc import ABC, abstractmethod
from pathlib import Path


class TextFileDetector(ABC):
    """Abstract class for detecting text files."""

    @abstractmethod
    def is_text_file(self, filename: str) -> bool:
        """Check if file is a text file."""

    @abstractmethod
    def get_extensions(self) -> set[str]:
        """Return set of text file extensions."""


class ExtensionBasedDetector(TextFileDetector):
    """Detects text files based on extensions."""

    def __init__(self, extensions: set[str] | None = None):
        """
        Initialize detector with extension set.

        Args:
            extensions: Set of text file extensions.
                       If None, default set is used.
        """
        self._extensions = extensions or self._get_default_extensions()

    def _get_default_extensions(self) -> set[str]:
        """Return default extension set."""
        return {
            # Source code
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".java",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".cs",
            ".go",
            ".rb",
            ".php",
            ".swift",
            ".kt",
            ".scala",
            ".rs",
            ".m",
            ".mm",
            # Web files
            ".html",
            ".css",
            ".scss",
            ".sass",
            ".less",
            ".json",
            ".xml",
            ".yaml",
            ".yml",
            # Configuration files
            ".env",
            ".gitignore",
            ".dockerignore",
            ".editorconfig",
            ".eslintrc",
            ".babelrc",
            ".prettierrc",
            ".npmrc",
            ".env.example",
            ".env.local",
            ".env.development",
            ".toml",  # TOML configuration (pyproject.toml, Cargo.toml, etc.)
            ".ini",  # INI configuration
            ".cfg",  # Configuration files
            ".conf",  # Configuration files
            ".properties",  # Java properties
            ".lock",  # Lock files (poetry.lock, package-lock.json without extension)
            ".pom",  # Maven POM
            ".gradle",  # Gradle scripts
            ".sbt",  # SBT configuration
            ".cmake",  # CMake files
            "Makefile",  # Makefile (no extension)
            ".makefile",  # Makefile with extension
            "Dockerfile",  # Dockerfile (no extension)
            ".dockerfile",  # Dockerfile with extension
            ".gitattributes",  # Git attributes
            ".gitconfig",  # Git config
            ".htaccess",  # Apache htaccess
            "nginx.conf",  # Nginx configuration
            ".clang-format",  # Clang format
            ".clang-tidy",  # Clang tidy
            ".cmakelists.txt",  # CMakeLists.txt
            ".flake8",  # Flake8 configuration
            ".pylintrc",  # Pylint configuration
            ".mypy.ini",  # MyPy configuration
            ".isort.cfg",  # isort configuration
            ".bandit",  # Bandit configuration
            ".coveragerc",  # Coverage configuration
            "setup.cfg",  # Setup configuration
            "tox.ini",  # Tox configuration
            ".pro",  # Qt project files
            ".qrc",  # Qt resource files
            ".ui",  # Qt UI files
            ".ts",  # Qt translation files (already in source code, but also used for configuration)
            # Documentation
            ".md",
            ".markdown",
            ".txt",
            ".rst",
            ".rdoc",
            ".tex",
            # Data
            ".csv",
            ".tsv",
            ".sql",
            ".log",
        }

    def is_text_file(self, filename: str) -> bool:
        """Check if file is a text file based on extension."""
        file_path = Path(filename.lower())
        return any(
            file_path.suffix == ext or file_path.name == ext for ext in self._extensions
        )

    def get_extensions(self) -> set[str]:
        """Return set of text file extensions."""
        return self._extensions.copy()

