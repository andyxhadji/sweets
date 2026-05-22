"""Tests for character encoding utilities."""

from sweets.core.characters import text_to_codes, codes_to_text, CHAR_MAP


def test_text_to_codes_letters():
    """A-Z should map to 1-26."""
    result = text_to_codes("ABC")
    assert result == [1, 2, 3]

    result = text_to_codes("XYZ")
    assert result == [24, 25, 26]


def test_text_to_codes_lowercase():
    """Lowercase letters should map same as uppercase."""
    result = text_to_codes("abc")
    assert result == [1, 2, 3]


def test_text_to_codes_digits():
    """Digits 1-9 map to 27-35, 0 maps to 36."""
    result = text_to_codes("123")
    assert result == [27, 28, 29]

    result = text_to_codes("0")
    assert result == [36]


def test_text_to_codes_punctuation():
    """Common punctuation should map correctly."""
    # ! is 37, space is 0
    result = text_to_codes("HI!")
    assert result == [8, 9, 37]

    # : is 44
    result = text_to_codes("12:30")
    assert result == [27, 28, 44, 29, 36]


def test_text_to_codes_unsupported():
    """Unsupported characters should become 0 (blank)."""
    # Emoji and special chars become blank
    result = text_to_codes("A★B")
    assert result == [1, 0, 2]


def test_codes_to_text_roundtrip():
    """Encoding then decoding should preserve supported text."""
    original = "HELLO WORLD"
    codes = text_to_codes(original)
    decoded = codes_to_text(codes)
    assert decoded == original
