"""Character encoding utilities for Vestaboard."""

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

# Reverse mapping for decoding
CODE_MAP: dict[int, str] = {v: k for k, v in CHAR_MAP.items()}
CODE_MAP[0] = " "  # Blank


def text_to_codes(text: str) -> list[int]:
    """Convert text to Vestaboard character codes.

    Unsupported characters become 0 (blank).
    """
    result = []
    for char in text.upper():
        code = CHAR_MAP.get(char, 0)
        result.append(code)
    return result


def codes_to_text(codes: list[int]) -> str:
    """Convert Vestaboard character codes to text."""
    return "".join(CODE_MAP.get(code, " ") for code in codes)
