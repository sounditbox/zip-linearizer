"""Тесты для CLI."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from zipfile import ZipFile

import pytest

from zip_linearizer.core.cli import main, ConsoleProgressReporter


class TestConsoleProgressReporter:
    """Тесты для ConsoleProgressReporter."""

    def test_report(self, capsys):
        """Тест отчета о прогрессе."""
        reporter = ConsoleProgressReporter()
        reporter.report(10, 5)
        captured = capsys.readouterr()
        assert "Обработано файлов: 10" in captured.err
        assert "пропущено: 5" in captured.err

    def test_report_error(self, capsys):
        """Тест отчета об ошибке."""
        reporter = ConsoleProgressReporter()
        reporter.report_error("test.py", "Error message")
        captured = capsys.readouterr()
        # В тихом режиме ошибки не выводятся в stdout, только логируются
        # Но мы можем проверить, что метод не вызывает исключение

    def test_report_verbose(self, capsys):
        """Тест отчета в verbose режиме."""
        reporter = ConsoleProgressReporter(verbose=True)
        reporter.report(10, 5)
        # В verbose режиме сообщения логируются, но не выводятся в stderr


class TestCLI:
    """Тесты для командной строки."""

    def test_main_with_nonexistent_file(self, capsys):
        """Тест обработки несуществующего файла."""
        with patch("sys.argv", ["zip-linearizer", "nonexistent.zip"]):
            result = main()
            assert result == 1
            captured = capsys.readouterr()
            assert "Ошибка" in captured.err or "не найден" in captured.err

    def test_main_with_invalid_args(self):
        """Тест обработки невалидных аргументов."""
        with patch("sys.argv", ["zip-linearizer"]):
            with pytest.raises(SystemExit):
                main()

    @patch("zip_linearizer.core.github_handler.GitHubRepositoryHandler")
    def test_main_with_github_url(self, mock_handler_class, capsys):
        """Тест работы с GitHub URL."""
        # Создаем временный ZIP файл для мока
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"
            with ZipFile(zip_path, "w") as zipf:
                zipf.writestr("test.py", "print('hello')")

            # Мокаем GitHub handler
            mock_handler = MagicMock()
            mock_handler.download_from_url.return_value = zip_path
            mock_handler_class.return_value = mock_handler

            with patch("sys.argv", ["zip-linearizer", "https://github.com/owner/repo"]):
                result = main()
                assert result == 0
                mock_handler.download_from_url.assert_called_once_with("https://github.com/owner/repo")

    @patch("zip_linearizer.core.github_handler.GitHubRepositoryHandler")
    def test_main_with_github_pull_request(self, mock_handler_class, capsys):
        """Тест работы с GitHub Pull Request URL."""
        # Создаем временный ZIP файл для мока
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"
            with ZipFile(zip_path, "w") as zipf:
                zipf.writestr("test.py", "print('hello')")

            # Мокаем GitHub handler
            mock_handler = MagicMock()
            mock_handler.download_from_url.return_value = zip_path
            mock_handler_class.return_value = mock_handler

            with patch("sys.argv", ["zip-linearizer", "https://github.com/owner/repo/pull/123"]):
                result = main()
                assert result == 0
                mock_handler.download_from_url.assert_called_once_with("https://github.com/owner/repo/pull/123")

    @patch("zip_linearizer.core.github_handler.GitHubRepositoryHandler")
    def test_main_with_github_pull_request_files(self, mock_handler_class, capsys):
        """Тест работы с GitHub Pull Request URL с /files."""
        # Создаем временный ZIP файл для мока
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"
            with ZipFile(zip_path, "w") as zipf:
                zipf.writestr("test.py", "print('hello')")

            # Мокаем GitHub handler
            mock_handler = MagicMock()
            mock_handler.download_from_url.return_value = zip_path
            mock_handler_class.return_value = mock_handler

            with patch("sys.argv", ["zip-linearizer", "https://github.com/owner/repo/pull/123/files"]):
                result = main()
                assert result == 0
                mock_handler.download_from_url.assert_called_once_with("https://github.com/owner/repo/pull/123/files")

    @patch("zip_linearizer.core.github_handler.GitHubRepositoryHandler")
    def test_main_with_github_url_error(self, mock_handler_class, capsys):
        """Тест обработки ошибки при работе с GitHub URL."""
        from zip_linearizer.core.exceptions import ProcessingError

        # Мокаем GitHub handler с ошибкой
        mock_handler = MagicMock()
        mock_handler.download_from_url.side_effect = ProcessingError("Repository not found")
        mock_handler_class.return_value = mock_handler

        with patch("sys.argv", ["zip-linearizer", "https://github.com/owner/repo"]):
            result = main()
            assert result == 1
            captured = capsys.readouterr()
            assert "Ошибка" in captured.err

    @patch("zip_linearizer.core.github_handler.GitHubRepositoryHandler")
    def test_main_with_github_url_cleanup_on_error(self, mock_handler_class, capsys):
        """Тест очистки временного файла при ошибке GitHub."""
        from zip_linearizer.core.exceptions import ProcessingError

        # Мокаем GitHub handler
        mock_handler = MagicMock()
        mock_handler.download_from_url.side_effect = ProcessingError("Repository not found")
        mock_handler_class.return_value = mock_handler

        with patch("sys.argv", ["zip-linearizer", "https://github.com/owner/repo"]):
            result = main()
            assert result == 1
            # Проверяем, что cleanup_temp_file не вызывается если файл не был скачан
            mock_handler.cleanup_temp_file.assert_not_called()

    @patch("zip_linearizer.core.github_handler.GitHubRepositoryHandler")
    def test_main_with_keep_temp_flag(self, mock_handler_class, capsys):
        """Тест работы с флагом --keep-temp для GitHub репозитория."""
        # Создаем временный ZIP файл для мока
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"
            with ZipFile(zip_path, "w") as zipf:
                zipf.writestr("test.py", "print('hello')")

            # Мокаем GitHub handler
            mock_handler = MagicMock()
            mock_handler.download_from_url.return_value = zip_path
            mock_handler_class.return_value = mock_handler

            with patch("sys.argv", ["zip-linearizer", "https://github.com/owner/repo", "--keep-temp"]):
                result = main()
                assert result == 0
                # Проверяем, что cleanup_temp_file не вызывается с флагом --keep-temp
                mock_handler.cleanup_temp_file.assert_not_called()

    def test_main_with_verbose_flag(self, capsys):
        """Тест работы с флагом verbose."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"
            output_path = Path(tmpdir) / "output.txt"

            with ZipFile(zip_path, "w") as zipf:
                zipf.writestr("test.py", "print('hello')")

            with patch("sys.argv", ["zip-linearizer", str(zip_path), "-v"]):
                result = main()
                assert result == 0

    def test_main_with_quiet_flag(self, capsys):
        """Тест работы с флагом quiet."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"
            output_path = Path(tmpdir) / "output.txt"

            with ZipFile(zip_path, "w") as zipf:
                zipf.writestr("test.py", "print('hello')")

            with patch("sys.argv", ["zip-linearizer", str(zip_path), "-q"]):
                result = main()
                assert result == 0
                captured = capsys.readouterr()
                # В quiet режиме не должно быть обычных сообщений
                assert "Обработка:" not in captured.err

