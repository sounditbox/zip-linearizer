"""Тесты для исключений."""

import pytest

from zip_linearizer.core.exceptions import (
    InvalidZipFileError,
    OutputError,
    ProcessingError,
    ZipLinearizerError,
)


class TestExceptions:
    """Тесты для исключений."""

    def test_zip_linearizer_error(self):
        """Тест базового исключения."""
        error = ZipLinearizerError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_invalid_zip_file_error(self):
        """Тест исключения для невалидного ZIP файла."""
        error = InvalidZipFileError("Invalid file")
        assert str(error) == "Invalid file"
        assert isinstance(error, ZipLinearizerError)

    def test_processing_error(self):
        """Тест исключения для ошибок обработки."""
        error = ProcessingError("Processing failed")
        assert str(error) == "Processing failed"
        assert isinstance(error, ZipLinearizerError)

    def test_output_error(self):
        """Тест исключения для ошибок вывода."""
        error = OutputError("Output failed")
        assert str(error) == "Output failed"
        assert isinstance(error, ZipLinearizerError)

    def test_exception_inheritance(self):
        """Тест иерархии исключений."""
        assert issubclass(InvalidZipFileError, ZipLinearizerError)
        assert issubclass(ProcessingError, ZipLinearizerError)
        assert issubclass(OutputError, ZipLinearizerError)
        assert issubclass(ZipLinearizerError, Exception)

