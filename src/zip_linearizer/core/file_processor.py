"""Module for processing files in ZIP archives."""

from pathlib import Path
from typing import Protocol

import zipfile

from zip_linearizer.config.settings import ProcessingSettings
from zip_linearizer.core.statistics import ProcessingStatistics
from zip_linearizer.core.text_file_detector import TextFileDetector
from zip_linearizer.core.validator import ZipValidator
from zip_linearizer.utils.decoder import ContentDecoder
from zip_linearizer.utils.logger import get_logger


class ProgressReporter(Protocol):
    """Protocol for reporting processing progress."""

    def report(self, processed: int, skipped: int) -> None:
        """Reports processing progress."""

    def report_error(self, filename: str, error: str) -> None:
        """Reports an error during file processing."""


class FileProcessor:
    """Processes files in ZIP archives."""

    def __init__(
        self,
        text_file_detector: TextFileDetector,
        decoder: ContentDecoder,
        settings: ProcessingSettings | None = None,
        progress_reporter: ProgressReporter | None = None,
    ):
        """
        Initialize the file processor.

        Args:
            text_file_detector: Text file detector.
            decoder: Content decoder.
            settings: Processing settings.
            progress_reporter: Progress reporter.
        """
        self._text_file_detector = text_file_detector
        self._decoder = decoder
        self._settings = settings or ProcessingSettings()
        self._progress_reporter = progress_reporter
        self._logger = get_logger(__name__)

    def process_zip(self, zip_path: Path, output_path: Path) -> ProcessingStatistics:
        """
        Process ZIP archive and create linearized file.

        Args:
            zip_path: Path to input ZIP file.
            output_path: Path to output file.

        Returns:
            Processing statistics.

        Raises:
            FileNotFoundError: If ZIP file is not found.
        """
        self._logger.info(f"Starting archive processing: {zip_path}")
        
        # Validate input file
        ZipValidator.validate(zip_path)
        
        stats = ProcessingStatistics()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref, open(
            output_path, "w", encoding="utf-8"
        ) as out_file:
            file_infos = sorted(zip_ref.infolist(), key=lambda x: x.filename)
            stats.total_files = len([f for f in file_infos if not f.is_dir()])
            stats.total_size = zip_path.stat().st_size

            processed_before_delimiter = 0

            for i, file_info in enumerate(file_infos):
                if file_info.is_dir():
                    continue

                if not self._text_file_detector.is_text_file(file_info.filename):
                    stats.skipped_files += 1
                    continue

                if processed_before_delimiter > 0:
                    out_file.write(self._settings.delimiter)

                self._write_file_header(out_file, file_info.filename)
                content = self._read_file_content(zip_ref, file_info, stats)
                
                if content:
                    out_file.write(content)
                    stats.processed_size += len(content.encode("utf-8"))
                    
                    if not content.endswith("\n"):
                        out_file.write("\n")

                if content:
                    stats.processed_files += 1
                    processed_before_delimiter += 1

                if (
                    self._progress_reporter
                    and stats.processed_files % self._settings.progress_report_interval == 0
                ):
                    self._progress_reporter.report(stats.processed_files, stats.skipped_files)

        if self._progress_reporter:
            self._progress_reporter.report(stats.processed_files, stats.skipped_files)

        self._logger.info(f"Processing completed. Statistics: {stats}")
        return stats

    def _write_file_header(self, out_file, filename: str) -> None:
        """Write file header to output file."""
        header = f"File: {filename}\n{self._settings.header_separator}\n\n"
        out_file.write(header)

    def _read_file_content(
        self, zip_ref: zipfile.ZipFile, file_info: zipfile.ZipInfo, stats: ProcessingStatistics
    ) -> str:
        """
        Read and decode file content from ZIP archive.

        Args:
            zip_ref: Opened ZIP archive.
            file_info: File information.
            stats: Processing statistics.

        Returns:
            Decoded file content.
        """
        try:
            with zip_ref.open(file_info) as f:
                content = f.read()
                decoded = self._decoder.decode(content)
                self._logger.debug(f"Processed file: {file_info.filename}")
                return decoded
        except Exception as e:
            stats.error_files += 1
            stats.error_filenames.append(file_info.filename)
            error_msg = f"Error reading {file_info.filename}: {str(e)}"
            self._logger.warning(error_msg)
            if self._progress_reporter:
                self._progress_reporter.report_error(file_info.filename, str(e))
            return ""

