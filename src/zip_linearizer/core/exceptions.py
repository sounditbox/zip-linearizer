"""Custom exceptions for Zip Linearizer."""


class ZipLinearizerError(Exception):
    """Base exception for all Zip Linearizer errors."""


class InvalidZipFileError(ZipLinearizerError):
    """Exception for invalid ZIP files."""


class ProcessingError(ZipLinearizerError):
    """Exception for processing errors."""


class OutputError(ZipLinearizerError):
    """Exception for output file write errors."""

