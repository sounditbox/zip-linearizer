"""Тесты для текстового детектора."""

import pytest

from zip_linearizer.core.text_file_detector import ExtensionBasedDetector


class TestExtensionBasedDetector:
    """Тесты для ExtensionBasedDetector."""

    def test_is_text_file_with_extension(self):
        """Тест определения текстового файла по расширению."""
        detector = ExtensionBasedDetector()
        assert detector.is_text_file("test.py") is True
        assert detector.is_text_file("test.js") is True
        assert detector.is_text_file("test.txt") is True
        assert detector.is_text_file("test.md") is True

    def test_is_text_file_without_extension(self):
        """Тест определения файла без расширения."""
        detector = ExtensionBasedDetector()
        assert detector.is_text_file("test") is False

    def test_is_text_file_binary(self):
        """Тест определения бинарных файлов."""
        detector = ExtensionBasedDetector()
        assert detector.is_text_file("test.exe") is False
        assert detector.is_text_file("test.dll") is False
        assert detector.is_text_file("test.zip") is False

    def test_is_text_file_case_insensitive(self):
        """Тест регистронезависимого определения."""
        detector = ExtensionBasedDetector()
        assert detector.is_text_file("test.PY") is True
        assert detector.is_text_file("TEST.JS") is True

    def test_is_text_file_with_config_extension(self):
        """Тест определения конфигурационных файлов."""
        detector = ExtensionBasedDetector()
        assert detector.is_text_file(".gitignore") is True
        assert detector.is_text_file(".env") is True
        assert detector.is_text_file("pyproject.toml") is True
        assert detector.is_text_file("config.ini") is True
        assert detector.is_text_file("setup.cfg") is True
        assert detector.is_text_file("Dockerfile") is True
        assert detector.is_text_file("Makefile") is True
        assert detector.is_text_file("nginx.conf") is True
        assert detector.is_text_file(".pylintrc") is True
        assert detector.is_text_file(".flake8") is True
        assert detector.is_text_file("poetry.lock") is True

    def test_get_extensions(self):
        """Тест получения расширений."""
        detector = ExtensionBasedDetector()
        extensions = detector.get_extensions()
        assert isinstance(extensions, set)
        assert ".py" in extensions
        assert ".txt" in extensions

    def test_custom_extensions(self):
        """Тест с пользовательскими расширениями."""
        custom_extensions = {".custom", ".special"}
        detector = ExtensionBasedDetector(custom_extensions)
        assert detector.is_text_file("test.custom") is True
        assert detector.is_text_file("test.special") is True
        assert detector.is_text_file("test.py") is False

