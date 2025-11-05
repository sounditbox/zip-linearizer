"""Тесты для декодера."""

import pytest

from zip_linearizer.utils.decoder import UTF8Decoder


class TestUTF8Decoder:
    """Тесты для UTF8Decoder."""

    def test_decode_utf8(self):
        """Тест декодирования UTF-8."""
        decoder = UTF8Decoder()
        content = "Привет, мир!".encode("utf-8")
        result = decoder.decode(content)
        assert result == "Привет, мир!"

    def test_decode_latin1_fallback(self):
        """Тест fallback на latin-1."""
        decoder = UTF8Decoder()
        # Создаем байты, которые не являются валидным UTF-8
        content = b"\x80\x81\x82"
        result = decoder.decode(content)
        # Должно декодироваться с latin-1
        assert isinstance(result, str)

    def test_decode_empty(self):
        """Тест декодирования пустого содержимого."""
        decoder = UTF8Decoder()
        result = decoder.decode(b"")
        assert result == ""

    def test_decode_ascii(self):
        """Тест декодирования ASCII."""
        decoder = UTF8Decoder()
        content = b"Hello, World!"
        result = decoder.decode(content)
        assert result == "Hello, World!"


