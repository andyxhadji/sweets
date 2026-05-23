"""Character encoding utilities for Vestaboard."""

import re

# Character to code mapping per Vestaboard spec
CHAR_MAP: dict[str, int] = {
    # Letters A-Z: 1-26
    **{chr(65 + i): i + 1 for i in range(26)},
    # Digits 1-9: 27-35, 0: 36
    **{str(i): 26 + i for i in range(1, 10)},
    "0": 36,
    # Punctuation: 37-60
    "!": 37,
    "@": 38,
    "#": 39,
    "$": 40,
    "(": 41,
    ")": 42,
    "-": 44,
    "+": 45,
    "&": 46,
    "=": 47,
    ";": 48,
    ":": 44,
    "'": 52,
    '"': 53,
    "%": 54,
    ",": 55,
    ".": 56,
    "/": 59,
    "?": 60,
    " ": 0,
}

# Special tokens for colors and icons (use {name} syntax in text)
SPECIAL_MAP: dict[str, int] = {
    # Icons
    "degree": 62,
    "heart": 62,
    "°": 62,
    "♥": 62,
    # Colors (each fills one cell)
    "red": 63,
    "orange": 64,
    "yellow": 65,
    "green": 66,
    "blue": 67,
    "violet": 68,
    "white": 69,
    "black": 70,
}

# Reverse mapping for decoding
CODE_MAP: dict[int, str] = {v: k for k, v in CHAR_MAP.items()}
CODE_MAP[0] = " "  # Blank
CODE_MAP[62] = "♥"
CODE_MAP[63] = "R"  # Red tile
CODE_MAP[64] = "O"  # Orange tile
CODE_MAP[65] = "Y"  # Yellow tile
CODE_MAP[66] = "G"  # Green tile
CODE_MAP[67] = "B"  # Blue tile
CODE_MAP[68] = "V"  # Violet tile
CODE_MAP[69] = "W"  # White tile
CODE_MAP[70] = "K"  # Black tile


def text_to_codes(text: str) -> list[int]:
    """Convert text to Vestaboard character codes.

    Supports special tokens like {red}, {heart}, {green} for colors and icons.
    Unsupported characters become 0 (blank).
    """
    result = []
    i = 0
    text_upper = text.upper()

    while i < len(text_upper):
        # Check for {special} tokens
        if text_upper[i] == "{":
            end = text_upper.find("}", i)
            if end != -1:
                token = text_upper[i + 1 : end].lower()
                if token in SPECIAL_MAP:
                    result.append(SPECIAL_MAP[token])
                    i = end + 1
                    continue
        # Regular character
        char = text_upper[i]
        code = CHAR_MAP.get(char, 0)
        result.append(code)
        i += 1

    return result


def codes_to_text(codes: list[int]) -> str:
    """Convert Vestaboard character codes to text."""
    return "".join(CODE_MAP.get(code, " ") for code in codes)
