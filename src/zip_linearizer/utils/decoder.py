"""Module for decoding file content."""

from abc import ABC, abstractmethod


class ContentDecoder(ABC):
    """Abstract class for decoding file content."""

    @abstractmethod
    def decode(self, content: bytes) -> str:
        """Decode byte content to string."""


class UTF8Decoder(ContentDecoder):
    """Decoder with UTF-8 support and fallback to latin-1."""

    def decode(self, content: bytes) -> str:
        """
        Decode content with UTF-8 priority.

        Args:
            content: File byte content.

        Returns:
            Decoded string.
        """
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1", errors="ignore")


