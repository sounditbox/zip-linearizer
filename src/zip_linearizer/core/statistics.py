"""Processing statistics."""

from dataclasses import dataclass, field


@dataclass
class ProcessingStatistics:
    """Statistics for ZIP archive processing."""

    total_files: int = 0
    processed_files: int = 0
    skipped_files: int = 0
    error_files: int = 0
    total_size: int = 0
    processed_size: int = 0
    error_filenames: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        """String representation of statistics."""
        return (
            f"Total files: {self.total_files}\n"
            f"Processed: {self.processed_files}\n"
            f"Skipped: {self.skipped_files}\n"
            f"Errors: {self.error_files}\n"
            f"Archive size: {self._format_size(self.total_size)}\n"
            f"Processed data: {self._format_size(self.processed_size)}"
        )

    @staticmethod
    def _format_size(size: int) -> str:
        """Format size in human-readable form."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

