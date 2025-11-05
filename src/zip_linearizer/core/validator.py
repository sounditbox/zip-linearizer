"""Input validation."""

import zipfile
from pathlib import Path

from zip_linearizer.core.exceptions import InvalidZipFileError


class ZipValidator:
    """ZIP file validator."""

    @staticmethod
    def validate(zip_path: Path) -> None:
        """
        Validate that file is a valid ZIP archive.

        Args:
            zip_path: Path to ZIP file.

        Raises:
            FileNotFoundError: If file does not exist.
            InvalidZipFileError: If file is not a valid ZIP archive.
        """
        if not zip_path.exists():
            raise FileNotFoundError(f"ZIP file not found: {zip_path}")

        if not zip_path.is_file():
            raise InvalidZipFileError(f"Path is not a file: {zip_path}")

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Check that archive can be opened and read
                zip_ref.testzip()
        except zipfile.BadZipFile:
            raise InvalidZipFileError(f"File is not a valid ZIP archive: {zip_path}")
        except Exception as e:
            raise InvalidZipFileError(f"Error checking ZIP archive: {e}")

