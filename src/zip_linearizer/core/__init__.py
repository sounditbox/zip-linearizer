"""Основные компоненты для обработки ZIP-архивов."""

from zip_linearizer.core.exceptions import (
    InvalidZipFileError,
    OutputError,
    ProcessingError,
    ZipLinearizerError,
)
from zip_linearizer.core.file_processor import FileProcessor, ProgressReporter
from zip_linearizer.core.github_handler import GitHubRepositoryHandler
from zip_linearizer.core.statistics import ProcessingStatistics
from zip_linearizer.core.text_file_detector import ExtensionBasedDetector, TextFileDetector
from zip_linearizer.core.validator import ZipValidator

__all__ = [
    "FileProcessor",
    "ProgressReporter",
    "TextFileDetector",
    "ExtensionBasedDetector",
    "ZipValidator",
    "GitHubRepositoryHandler",
    "ProcessingStatistics",
    "ZipLinearizerError",
    "InvalidZipFileError",
    "ProcessingError",
    "OutputError",
]


