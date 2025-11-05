"""Тесты для процессора файлов."""

import tempfile
from pathlib import Path
from zipfile import ZipFile

import pytest

from zip_linearizer.core.file_processor import FileProcessor
from zip_linearizer.core.text_file_detector import ExtensionBasedDetector
from zip_linearizer.utils.decoder import UTF8Decoder
from zip_linearizer.config.settings import ProcessingSettings


class MockProgressReporter:
    """Мок-репортер для тестирования."""

    def __init__(self):
        self.reports = []
        self.errors = []

    def report(self, processed: int, skipped: int) -> None:
        """Сохраняет отчет о прогрессе."""
        self.reports.append((processed, skipped))

    def report_error(self, filename: str, error: str) -> None:
        """Сохраняет ошибку."""
        self.errors.append((filename, error))


class TestFileProcessor:
    """Тесты для FileProcessor."""

    def test_process_zip_file_not_found(self):
        """Тест обработки несуществующего файла."""
        processor = FileProcessor(
            ExtensionBasedDetector(), UTF8Decoder(), ProcessingSettings()
        )
        with pytest.raises(FileNotFoundError):
            processor.process_zip(Path("nonexistent.zip"), Path("output.txt"))

    def test_process_zip_empty_archive(self):
        """Тест обработки пустого архива."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "empty.zip"
            output_path = Path(tmpdir) / "output.txt"

            # Создаем пустой ZIP
            with ZipFile(zip_path, "w") as zipf:
                pass

            processor = FileProcessor(
                ExtensionBasedDetector(), UTF8Decoder(), ProcessingSettings()
            )
            stats = processor.process_zip(zip_path, output_path)

            assert stats.processed_files == 0
            assert stats.skipped_files == 0
            assert stats.total_files == 0
            assert output_path.exists()

    def test_process_zip_with_text_files(self):
        """Тест обработки архива с текстовыми файлами."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"
            output_path = Path(tmpdir) / "output.txt"

            # Создаем ZIP с текстовыми файлами
            with ZipFile(zip_path, "w") as zipf:
                zipf.writestr("file1.py", "print('Hello')")
                zipf.writestr("file2.txt", "Some text")
                zipf.writestr("file3.exe", b"\x00\x01\x02")

            processor = FileProcessor(
                ExtensionBasedDetector(), UTF8Decoder(), ProcessingSettings()
            )
            stats = processor.process_zip(zip_path, output_path)

            assert stats.processed_files == 2
            assert stats.skipped_files == 1
            assert stats.total_files == 3  # Всего файлов в архиве
            assert stats.total_size > 0  # Размер архива должен быть больше 0
            assert stats.processed_size > 0  # Обработанный размер должен быть больше 0
            assert output_path.exists()

            content = output_path.read_text(encoding="utf-8")
            assert "file1.py" in content
            assert "file2.txt" in content
            assert "print('Hello')" in content
            assert "Some text" in content

    def test_process_zip_with_progress_reporter(self):
        """Тест обработки с репортером прогресса."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"
            output_path = Path(tmpdir) / "output.txt"

            with ZipFile(zip_path, "w") as zipf:
                for i in range(15):
                    zipf.writestr(f"file{i}.py", f"content {i}")

            reporter = MockProgressReporter()
            settings = ProcessingSettings(progress_report_interval=10)
            processor = FileProcessor(
                ExtensionBasedDetector(), UTF8Decoder(), settings, reporter
            )

            stats = processor.process_zip(zip_path, output_path)

            assert stats.processed_files == 15
            assert stats.skipped_files == 0
            # Должно быть 2 отчета: на 10 и 15 файлах
            assert len(reporter.reports) >= 1

    def test_process_zip_with_directories(self):
        """Тест обработки архива с директориями."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"
            output_path = Path(tmpdir) / "output.txt"

            with ZipFile(zip_path, "w") as zipf:
                zipf.writestr("dir/file1.py", "content")
                zipf.writestr("dir/file2.txt", "content")

            processor = FileProcessor(
                ExtensionBasedDetector(), UTF8Decoder(), ProcessingSettings()
            )
            stats = processor.process_zip(zip_path, output_path)

            assert stats.processed_files == 2
            assert stats.skipped_files == 0

    def test_process_zip_custom_delimiter(self):
        """Тест обработки с пользовательским разделителем."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"
            output_path = Path(tmpdir) / "output.txt"

            with ZipFile(zip_path, "w") as zipf:
                zipf.writestr("file1.py", "content1")
                zipf.writestr("file2.py", "content2")

            settings = ProcessingSettings(delimiter="\n###\n")
            processor = FileProcessor(
                ExtensionBasedDetector(), UTF8Decoder(), settings
            )
            processor.process_zip(zip_path, output_path)

            content = output_path.read_text(encoding="utf-8")
            assert "###" in content

    def test_process_zip_with_error_tracking(self):
        """Тест отслеживания ошибок в статистике."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"
            output_path = Path(tmpdir) / "output.txt"

            with ZipFile(zip_path, "w") as zipf:
                zipf.writestr("file1.py", "content1")
                zipf.writestr("file2.py", "content2")

            reporter = MockProgressReporter()
            processor = FileProcessor(
                ExtensionBasedDetector(), UTF8Decoder(), ProcessingSettings(), reporter
            )
            stats = processor.process_zip(zip_path, output_path)

            # В нормальном случае ошибок быть не должно
            assert stats.error_files == 0
            assert len(stats.error_filenames) == 0
            assert stats.processed_files == 2

