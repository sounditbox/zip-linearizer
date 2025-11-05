"""Тесты для статистики обработки."""

from zip_linearizer.core.statistics import ProcessingStatistics


class TestProcessingStatistics:
    """Тесты для ProcessingStatistics."""

    def test_default_statistics(self):
        """Тест статистики по умолчанию."""
        stats = ProcessingStatistics()
        assert stats.total_files == 0
        assert stats.processed_files == 0
        assert stats.skipped_files == 0
        assert stats.error_files == 0
        assert stats.total_size == 0
        assert stats.processed_size == 0
        assert stats.error_filenames == []

    def test_statistics_with_data(self):
        """Тест статистики с данными."""
        stats = ProcessingStatistics(
            total_files=10,
            processed_files=8,
            skipped_files=1,
            error_files=1,
            total_size=1024,
            processed_size=512,
            error_filenames=["error.txt"],
        )
        assert stats.total_files == 10
        assert stats.processed_files == 8
        assert stats.skipped_files == 1
        assert stats.error_files == 1
        assert stats.total_size == 1024
        assert stats.processed_size == 512
        assert len(stats.error_filenames) == 1
        assert "error.txt" in stats.error_filenames

    def test_format_size_bytes(self):
        """Тест форматирования размера в байтах."""
        stats = ProcessingStatistics()
        assert stats._format_size(512) == "512.00 B"

    def test_format_size_kb(self):
        """Тест форматирования размера в килобайтах."""
        stats = ProcessingStatistics()
        assert "KB" in stats._format_size(2048)

    def test_format_size_mb(self):
        """Тест форматирования размера в мегабайтах."""
        stats = ProcessingStatistics()
        assert "MB" in stats._format_size(2 * 1024 * 1024)

    def test_statistics_string_representation(self):
        """Тест строкового представления статистики."""
        stats = ProcessingStatistics(
            total_files=10,
            processed_files=8,
            skipped_files=1,
            error_files=1,
            total_size=1024,
            processed_size=512,
        )
        stats_str = str(stats)
        assert "Всего файлов: 10" in stats_str
        assert "Обработано: 8" in stats_str
        assert "Пропущено: 1" in stats_str
        assert "Ошибок: 1" in stats_str

