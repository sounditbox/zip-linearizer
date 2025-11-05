"""Тесты для валидатора ZIP файлов."""

import tempfile
from pathlib import Path
from zipfile import ZipFile

import pytest

from zip_linearizer.core.exceptions import InvalidZipFileError
from zip_linearizer.core.validator import ZipValidator


class TestZipValidator:
    """Тесты для ZipValidator."""

    def test_validate_valid_zip(self):
        """Тест валидации валидного ZIP файла."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "valid.zip"
            with ZipFile(zip_path, "w") as zipf:
                zipf.writestr("test.txt", "content")

            # Не должно вызывать исключение
            ZipValidator.validate(zip_path)

    def test_validate_nonexistent_file(self):
        """Тест валидации несуществующего файла."""
        with pytest.raises(FileNotFoundError):
            ZipValidator.validate(Path("nonexistent.zip"))

    def test_validate_directory(self):
        """Тест валидации директории вместо файла."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)
            with pytest.raises(InvalidZipFileError):
                ZipValidator.validate(dir_path)

    def test_validate_invalid_zip(self):
        """Тест валидации невалидного ZIP файла."""
        with tempfile.TemporaryDirectory() as tmpdir:
            invalid_zip = Path(tmpdir) / "invalid.zip"
            # Создаем файл, который не является ZIP
            invalid_zip.write_text("This is not a zip file")

            with pytest.raises(InvalidZipFileError):
                ZipValidator.validate(invalid_zip)

    def test_validate_empty_file(self):
        """Тест валидации пустого файла."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_file = Path(tmpdir) / "empty.zip"
            empty_file.touch()

            with pytest.raises(InvalidZipFileError):
                ZipValidator.validate(empty_file)

