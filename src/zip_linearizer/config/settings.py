"""Application settings."""

from dataclasses import dataclass


@dataclass
class ProcessingSettings:
    """Settings for ZIP archive processing."""

    delimiter: str = "\n---\n"
    progress_report_interval: int = 10
    header_separator: str = "=" * 80


