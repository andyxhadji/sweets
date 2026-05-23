# Vestaboard Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python platform for controlling Vestaboard displays with modular modes, web UI, and terminal UI.

**Architecture:** Plugin-based mode system with auto-discovery. Core layer handles character encoding and API communication. Scheduler manages single active mode. Flask web UI and Textual TUI provide user interfaces.

**Tech Stack:** Python 3.11+, requests, PyYAML, Flask, Textual, pytest, responses

---

## File Structure

```
sweets/
├── pyproject.toml              # Project metadata, dependencies, entry points
├── config.yaml                 # Main configuration (committed)
├── secrets.yaml                # API tokens (gitignored)
├── .gitignore                  # Ignore secrets, __pycache__, etc.
├── sweets/
│   ├── __init__.py             # Package marker
│   ├── config.py               # Config loader
│   ├── scheduler.py            # Mode runner with background thread
│   ├── core/
│   │   ├── __init__.py         # Package marker
│   │   ├── characters.py       # Character encoding utilities
│   │   ├── board.py            # Board abstraction (6x22 grid)
│   │   └── api.py              # Vestaboard API client
│   ├── modes/
│   │   ├── __init__.py         # Package marker
│   │   ├── base.py             # Abstract Mode class
│   │   ├── registry.py         # Auto-discovery of modes
│   │   └── clock.py            # Clock mode implementation
│   ├── web/
│   │   ├── __init__.py         # Package marker
│   │   ├── app.py              # Flask application
│   │   └── templates/
│   │       ├── base.html       # Base layout
│   │       └── index.html      # Dashboard
│   └── tui/
│       ├── __init__.py         # Package marker
│       └── app.py              # Textual application
└── tests/
    ├── __init__.py             # Package marker
    ├── conftest.py             # Shared fixtures
    ├── test_characters.py      # Character encoding tests
    ├── test_board.py           # Board abstraction tests
    ├── test_api.py             # API client integration tests
    └── modes/
        ├── __init__.py         # Package marker
        └── test_clock.py       # Clock mode tests
```

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `config.yaml`
- Create: `secrets.yaml.example`
- Create: `sweets/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "sweets"
version = "0.1.0"
description = "A Vestaboard Platform"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
    "pyyaml>=6.0",
    "flask>=3.0.0",
    "textual>=0.50.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "responses>=0.25.0",
]

[project.scripts]
sweets-web = "sweets.web.app:main"
sweets-tui = "sweets.tui.app:main"
```

- [ ] **Step 2: Create .gitignore**

```
# Secrets
secrets.yaml

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
```

- [ ] **Step 3: Create config.yaml**

```yaml
api:
  type: cloud
  host: vestaboard.local

default_mode: clock

modes:
  clock:
    format: 12h
    show_seconds: false

web:
  host: 127.0.0.1
  port: 5000
```

- [ ] **Step 4: Create secrets.yaml.example**

```yaml
# Copy this file to secrets.yaml and fill in your API tokens
# DO NOT commit secrets.yaml to version control

cloud_api_token: "your-cloud-api-token-here"
local_api_key: "your-local-api-key-here"
```

- [ ] **Step 5: Create sweets/__init__.py**

```python
"""Sweets - A Vestaboard Platform."""

__version__ = "0.1.0"
```

- [ ] **Step 6: Create virtual environment and install dependencies**

Run:
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
```

Expected: Installation completes with no errors

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .gitignore config.yaml secrets.yaml.example sweets/__init__.py
git commit -m "feat: project setup with dependencies and config structure"
```

---

## Task 2: Character Encoding

**Files:**
- Create: `sweets/core/__init__.py`
- Create: `sweets/core/characters.py`
- Create: `tests/__init__.py`
- Create: `tests/test_characters.py`

- [ ] **Step 1: Create package markers**

Create `sweets/core/__init__.py`:
```python
"""Core components for Vestaboard communication."""
```

Create `tests/__init__.py`:
```python
"""Test suite for sweets."""
```

- [ ] **Step 2: Write failing test for letter encoding**

Create `tests/test_characters.py`:
```python
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
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_characters.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'sweets.core.characters'"

- [ ] **Step 4: Write minimal implementation for letters**

Create `sweets/core/characters.py`:
```python
"""Character encoding utilities for Vestaboard."""

# Character to code mapping per Vestaboard spec
CHAR_MAP: dict[str, int] = {
    # Letters A-Z: 1-26
    **{chr(65 + i): i + 1 for i in range(26)},
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_characters.py -v`

Expected: PASS

- [ ] **Step 6: Add test for digits**

Add to `tests/test_characters.py`:
```python
def test_text_to_codes_digits():
    """Digits 1-9 map to 27-35, 0 maps to 36."""
    result = text_to_codes("123")
    assert result == [27, 28, 29]

    result = text_to_codes("0")
    assert result == [36]
```

- [ ] **Step 7: Run test to verify it fails**

Run: `pytest tests/test_characters.py::test_text_to_codes_digits -v`

Expected: FAIL (digits not yet mapped)

- [ ] **Step 8: Add digit mapping**

Update `sweets/core/characters.py` CHAR_MAP:
```python
CHAR_MAP: dict[str, int] = {
    # Letters A-Z: 1-26
    **{chr(65 + i): i + 1 for i in range(26)},
    # Digits 1-9: 27-35, 0: 36
    **{str(i): 26 + i for i in range(1, 10)},
    "0": 36,
}
```

- [ ] **Step 9: Run test to verify it passes**

Run: `pytest tests/test_characters.py::test_text_to_codes_digits -v`

Expected: PASS

- [ ] **Step 10: Add test for punctuation**

Add to `tests/test_characters.py`:
```python
def test_text_to_codes_punctuation():
    """Common punctuation should map correctly."""
    # ! is 37, space is 0
    result = text_to_codes("HI!")
    assert result == [8, 9, 37]

    # : is 44
    result = text_to_codes("12:30")
    assert result == [27, 28, 44, 29, 36]
```

- [ ] **Step 11: Run test to verify it fails**

Run: `pytest tests/test_characters.py::test_text_to_codes_punctuation -v`

Expected: FAIL (punctuation not yet mapped)

- [ ] **Step 12: Add punctuation mapping**

Update `sweets/core/characters.py` CHAR_MAP:
```python
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
```

- [ ] **Step 13: Run test to verify it passes**

Run: `pytest tests/test_characters.py::test_text_to_codes_punctuation -v`

Expected: PASS

- [ ] **Step 14: Add test for unsupported characters**

Add to `tests/test_characters.py`:
```python
def test_text_to_codes_unsupported():
    """Unsupported characters should become 0 (blank)."""
    # Emoji and special chars become blank
    result = text_to_codes("A★B")
    assert result == [1, 0, 2]
```

- [ ] **Step 15: Run test to verify it passes**

Run: `pytest tests/test_characters.py::test_text_to_codes_unsupported -v`

Expected: PASS (already handled by default in text_to_codes)

- [ ] **Step 16: Add roundtrip test**

Add to `tests/test_characters.py`:
```python
def test_codes_to_text_roundtrip():
    """Encoding then decoding should preserve supported text."""
    original = "HELLO WORLD"
    codes = text_to_codes(original)
    decoded = codes_to_text(codes)
    assert decoded == original
```

- [ ] **Step 17: Run all character tests**

Run: `pytest tests/test_characters.py -v`

Expected: All tests PASS

- [ ] **Step 18: Commit**

```bash
git add sweets/core/__init__.py sweets/core/characters.py tests/__init__.py tests/test_characters.py
git commit -m "feat: character encoding utilities with full mapping"
```

---

## Task 3: Board Abstraction

**Files:**
- Create: `sweets/core/board.py`
- Create: `tests/test_board.py`

- [ ] **Step 1: Write failing test for board dimensions**

Create `tests/test_board.py`:
```python
"""Tests for Board abstraction."""

from sweets.core.board import Board


def test_board_dimensions():
    """Board should always be 6 rows x 22 columns."""
    board = Board()
    assert len(board.rows) == 6
    for row in board.rows:
        assert len(row) == 22
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_board.py::test_board_dimensions -v`

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Write minimal Board class**

Create `sweets/core/board.py`:
```python
"""Board abstraction for Vestaboard's 6x22 grid."""

from sweets.core.characters import text_to_codes, codes_to_text

ROWS = 6
COLS = 22


class Board:
    """Represents a Vestaboard's 6x22 character grid."""

    def __init__(self) -> None:
        """Initialize an empty board (all blanks)."""
        self.rows: list[list[int]] = [[0] * COLS for _ in range(ROWS)]

    def to_array(self) -> list[list[int]]:
        """Return API-ready 6x22 nested list."""
        return [row[:] for row in self.rows]

    def clear(self) -> None:
        """Reset all cells to blank (0)."""
        self.rows = [[0] * COLS for _ in range(ROWS)]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_board.py::test_board_dimensions -v`

Expected: PASS

- [ ] **Step 5: Add test for to_array format**

Add to `tests/test_board.py`:
```python
def test_to_array_format():
    """to_array should return a copy of the grid."""
    board = Board()
    board.rows[0][0] = 1  # Set 'A'

    array = board.to_array()
    assert array[0][0] == 1

    # Modifying returned array shouldn't affect board
    array[0][0] = 99
    assert board.rows[0][0] == 1
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/test_board.py::test_to_array_format -v`

Expected: PASS

- [ ] **Step 7: Add test for set_row**

Add to `tests/test_board.py`:
```python
def test_set_row():
    """set_row should replace a row, padding or truncating as needed."""
    board = Board()

    # Set row with exact length
    codes = [1, 2, 3] + [0] * 19  # 22 chars
    board.set_row(0, codes)
    assert board.rows[0] == codes

    # Set row with shorter list (should pad with 0s)
    board.set_row(1, [1, 2, 3])
    assert board.rows[1] == [1, 2, 3] + [0] * 19
```

- [ ] **Step 8: Run test to verify it fails**

Run: `pytest tests/test_board.py::test_set_row -v`

Expected: FAIL (set_row not implemented)

- [ ] **Step 9: Implement set_row**

Add to `sweets/core/board.py` Board class:
```python
    def set_row(self, index: int, codes: list[int]) -> None:
        """Set a specific row, padding or truncating to 22 chars."""
        if index < 0 or index >= ROWS:
            raise IndexError(f"Row index must be 0-{ROWS - 1}")
        # Pad with zeros if too short, truncate if too long
        padded = (codes + [0] * COLS)[:COLS]
        self.rows[index] = padded
```

- [ ] **Step 10: Run test to verify it passes**

Run: `pytest tests/test_board.py::test_set_row -v`

Expected: PASS

- [ ] **Step 11: Add test for center_text**

Add to `tests/test_board.py`:
```python
def test_center_text():
    """center_text should center text on a row."""
    board = Board()

    # "HI" is 2 chars, should have 10 blanks on each side
    board.center_text(0, "HI")
    expected = [0] * 10 + [8, 9] + [0] * 10
    assert board.rows[0] == expected
```

- [ ] **Step 12: Run test to verify it fails**

Run: `pytest tests/test_board.py::test_center_text -v`

Expected: FAIL (center_text not implemented)

- [ ] **Step 13: Implement center_text**

Add to `sweets/core/board.py` Board class:
```python
    def center_text(self, row: int, text: str) -> None:
        """Center text on a row."""
        codes = text_to_codes(text)
        if len(codes) >= COLS:
            self.set_row(row, codes[:COLS])
            return
        padding = (COLS - len(codes)) // 2
        centered = [0] * padding + codes + [0] * (COLS - padding - len(codes))
        self.set_row(row, centered)
```

- [ ] **Step 14: Run test to verify it passes**

Run: `pytest tests/test_board.py::test_center_text -v`

Expected: PASS

- [ ] **Step 15: Add test for from_text simple**

Add to `tests/test_board.py`:
```python
def test_from_text_simple():
    """from_text should center short messages."""
    board = Board.from_text("HI")

    # "HI" should be centered on middle row (row 2 or 3)
    # Check that HI appears somewhere centered
    found = False
    for row in board.rows:
        text = "".join(chr(64 + c) if 1 <= c <= 26 else " " for c in row).strip()
        if text == "HI":
            found = True
            break
    assert found, "HI should appear centered on the board"
```

- [ ] **Step 16: Run test to verify it fails**

Run: `pytest tests/test_board.py::test_from_text_simple -v`

Expected: FAIL (from_text not implemented)

- [ ] **Step 17: Implement from_text**

Add to `sweets/core/board.py` Board class:
```python
    @classmethod
    def from_text(cls, message: str) -> "Board":
        """Create a board from text with word wrapping and centering."""
        board = cls()
        words = message.upper().split()

        if not words:
            return board

        # Build lines that fit within COLS
        lines: list[str] = []
        current_line = ""

        for word in words:
            if not current_line:
                current_line = word
            elif len(current_line) + 1 + len(word) <= COLS:
                current_line += " " + word
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # Center lines vertically
        start_row = max(0, (ROWS - len(lines)) // 2)

        for i, line in enumerate(lines[:ROWS]):
            board.center_text(start_row + i, line)

        return board
```

- [ ] **Step 18: Run test to verify it passes**

Run: `pytest tests/test_board.py::test_from_text_simple -v`

Expected: PASS

- [ ] **Step 19: Add test for from_text wrapping**

Add to `tests/test_board.py`:
```python
def test_from_text_wrapping():
    """from_text should wrap long text to multiple lines."""
    # 30 chars won't fit on one line (max 22)
    board = Board.from_text("THE QUICK BROWN FOX JUMPS")

    # Should have content on multiple rows
    non_empty_rows = sum(1 for row in board.rows if any(c != 0 for c in row))
    assert non_empty_rows >= 2, "Long text should wrap to multiple rows"
```

- [ ] **Step 20: Run test to verify it passes**

Run: `pytest tests/test_board.py::test_from_text_wrapping -v`

Expected: PASS

- [ ] **Step 21: Run all board tests**

Run: `pytest tests/test_board.py -v`

Expected: All tests PASS

- [ ] **Step 22: Commit**

```bash
git add sweets/core/board.py tests/test_board.py
git commit -m "feat: Board abstraction with text centering and wrapping"
```

---

## Task 4: Vestaboard API Client

**Files:**
- Create: `sweets/core/api.py`
- Create: `tests/conftest.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Create test fixtures**

Create `tests/conftest.py`:
```python
"""Shared test fixtures."""

import pytest
import responses

from sweets.core.board import Board


@pytest.fixture
def sample_board() -> Board:
    """A board with 'HI' centered."""
    board = Board()
    board.center_text(2, "HI")
    return board


@pytest.fixture
def sample_board_array() -> list[list[int]]:
    """API response format for a board with 'HI'."""
    rows = [[0] * 22 for _ in range(6)]
    rows[2] = [0] * 10 + [8, 9] + [0] * 10
    return rows


@pytest.fixture
def mock_cloud_api():
    """Activate responses mock for Vestaboard Cloud API."""
    with responses.RequestsMock() as rsps:
        yield rsps
```

- [ ] **Step 2: Write failing test for CloudClient read**

Create `tests/test_api.py`:
```python
"""Tests for Vestaboard API client."""

import responses

from sweets.core.api import CloudClient
from sweets.core.board import Board


def test_cloud_client_read(mock_cloud_api, sample_board_array):
    """CloudClient.read() should return a Board from API response."""
    mock_cloud_api.add(
        responses.GET,
        "https://cloud.vestaboard.com/",
        json={"currentMessage": {"layout": sample_board_array}},
        status=200,
    )

    client = CloudClient(api_token="test-token")
    board = client.read()

    assert isinstance(board, Board)
    assert board.rows[2][10] == 8  # 'H'
    assert board.rows[2][11] == 9  # 'I'
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_api.py::test_cloud_client_read -v`

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 4: Write minimal CloudClient**

Create `sweets/core/api.py`:
```python
"""Vestaboard API client implementations."""

from abc import ABC, abstractmethod

import requests

from sweets.core.board import Board, ROWS, COLS


class VestaboardClient(ABC):
    """Abstract base class for Vestaboard API clients."""

    @abstractmethod
    def read(self) -> Board:
        """Get current board state."""
        pass

    @abstractmethod
    def write(self, board: Board) -> bool:
        """Send board state, return success."""
        pass


class CloudClient(VestaboardClient):
    """Vestaboard Cloud API client at https://cloud.vestaboard.com."""

    def __init__(self, api_token: str) -> None:
        self.api_token = api_token
        self.base_url = "https://cloud.vestaboard.com"

    def _headers(self) -> dict[str, str]:
        return {
            "X-Vestaboard-Token": self.api_token,
            "Content-Type": "application/json",
        }

    def read(self) -> Board:
        """Get current board state from API."""
        response = requests.get(f"{self.base_url}/", headers=self._headers())
        response.raise_for_status()

        data = response.json()
        layout = data.get("currentMessage", {}).get("layout", [])

        board = Board()
        for i, row in enumerate(layout[:ROWS]):
            board.set_row(i, row[:COLS])

        return board

    def write(self, board: Board) -> bool:
        """Send board state to API."""
        raise NotImplementedError("write not yet implemented")
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_api.py::test_cloud_client_read -v`

Expected: PASS

- [ ] **Step 6: Add test for CloudClient write**

Add to `tests/test_api.py`:
```python
def test_cloud_client_write(mock_cloud_api, sample_board):
    """CloudClient.write() should POST board as characters array."""
    mock_cloud_api.add(
        responses.POST,
        "https://cloud.vestaboard.com/",
        json={"status": "ok"},
        status=200,
    )

    client = CloudClient(api_token="test-token")
    result = client.write(sample_board)

    assert result is True

    # Verify the request body
    request_body = mock_cloud_api.calls[0].request.body
    assert b'"characters"' in request_body
```

- [ ] **Step 7: Run test to verify it fails**

Run: `pytest tests/test_api.py::test_cloud_client_write -v`

Expected: FAIL (NotImplementedError)

- [ ] **Step 8: Implement write method**

Update `sweets/core/api.py` CloudClient.write:
```python
    def write(self, board: Board) -> bool:
        """Send board state to API."""
        payload = {"characters": board.to_array()}
        response = requests.post(
            f"{self.base_url}/",
            headers=self._headers(),
            json=payload,
        )
        response.raise_for_status()
        return True
```

- [ ] **Step 9: Run test to verify it passes**

Run: `pytest tests/test_api.py::test_cloud_client_write -v`

Expected: PASS

- [ ] **Step 10: Add test for auth header**

Add to `tests/test_api.py`:
```python
def test_cloud_client_auth_header(mock_cloud_api, sample_board_array):
    """CloudClient should include X-Vestaboard-Token header."""
    mock_cloud_api.add(
        responses.GET,
        "https://cloud.vestaboard.com/",
        json={"currentMessage": {"layout": sample_board_array}},
        status=200,
    )

    client = CloudClient(api_token="my-secret-token")
    client.read()

    request_headers = mock_cloud_api.calls[0].request.headers
    assert request_headers["X-Vestaboard-Token"] == "my-secret-token"
    assert request_headers["Content-Type"] == "application/json"
```

- [ ] **Step 11: Run test to verify it passes**

Run: `pytest tests/test_api.py::test_cloud_client_auth_header -v`

Expected: PASS

- [ ] **Step 12: Add test for error handling**

Add to `tests/test_api.py`:
```python
import pytest


def test_cloud_client_error_handling(mock_cloud_api):
    """CloudClient should raise on API errors."""
    mock_cloud_api.add(
        responses.GET,
        "https://cloud.vestaboard.com/",
        json={"error": "Unauthorized"},
        status=401,
    )

    client = CloudClient(api_token="bad-token")

    with pytest.raises(requests.HTTPError):
        client.read()
```

- [ ] **Step 13: Run test to verify it passes**

Run: `pytest tests/test_api.py::test_cloud_client_error_handling -v`

Expected: PASS

- [ ] **Step 14: Add LocalClient stub**

Add to `sweets/core/api.py`:
```python
class LocalClient(VestaboardClient):
    """Vestaboard Local API client (stubbed for future implementation)."""

    def __init__(self, api_key: str, host: str = "vestaboard.local") -> None:
        self.api_key = api_key
        self.base_url = f"http://{host}:7000"

    def read(self) -> Board:
        """Get current board state from local API."""
        raise NotImplementedError("LocalClient not yet implemented")

    def write(self, board: Board) -> bool:
        """Send board state to local API."""
        raise NotImplementedError("LocalClient not yet implemented")
```

- [ ] **Step 15: Run all API tests**

Run: `pytest tests/test_api.py -v`

Expected: All tests PASS

- [ ] **Step 16: Commit**

```bash
git add sweets/core/api.py tests/conftest.py tests/test_api.py
git commit -m "feat: Vestaboard Cloud API client with read/write"
```

---

## Task 5: Configuration Loader

**Files:**
- Create: `sweets/config.py`

- [ ] **Step 1: Create config loader**

Create `sweets/config.py`:
```python
"""Configuration loading and validation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Config:
    """Application configuration."""

    api_type: str = "cloud"
    api_host: str = "vestaboard.local"
    cloud_api_token: str = ""
    local_api_key: str | None = None
    default_mode: str = "clock"
    modes: dict[str, dict[str, Any]] = field(default_factory=dict)
    web_host: str = "127.0.0.1"
    web_port: int = 5000


def load_config(
    config_path: Path | None = None,
    secrets_path: Path | None = None,
) -> Config:
    """Load configuration from config.yaml and secrets.yaml.

    Args:
        config_path: Path to config.yaml (defaults to ./config.yaml)
        secrets_path: Path to secrets.yaml (defaults to ./secrets.yaml)

    Returns:
        Validated Config object

    Raises:
        FileNotFoundError: If config files don't exist
        ValueError: If required fields are missing
    """
    if config_path is None:
        config_path = Path("config.yaml")
    if secrets_path is None:
        secrets_path = Path("secrets.yaml")

    # Load main config
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config_data = yaml.safe_load(f) or {}

    # Load secrets (optional - may not exist yet)
    secrets_data: dict[str, Any] = {}
    if secrets_path.exists():
        with open(secrets_path) as f:
            secrets_data = yaml.safe_load(f) or {}

    # Build config object
    api_config = config_data.get("api", {})
    web_config = config_data.get("web", {})

    config = Config(
        api_type=api_config.get("type", "cloud"),
        api_host=api_config.get("host", "vestaboard.local"),
        cloud_api_token=secrets_data.get("cloud_api_token", ""),
        local_api_key=secrets_data.get("local_api_key"),
        default_mode=config_data.get("default_mode", "clock"),
        modes=config_data.get("modes", {}),
        web_host=web_config.get("host", "127.0.0.1"),
        web_port=web_config.get("port", 5000),
    )

    return config
```

- [ ] **Step 2: Verify config loads**

Run:
```bash
python -c "from sweets.config import load_config; c = load_config(); print(f'API type: {c.api_type}, default mode: {c.default_mode}')"
```

Expected: `API type: cloud, default mode: clock`

- [ ] **Step 3: Commit**

```bash
git add sweets/config.py
git commit -m "feat: configuration loader for YAML files"
```

---

## Task 6: Mode Framework

**Files:**
- Create: `sweets/modes/__init__.py`
- Create: `sweets/modes/base.py`
- Create: `sweets/modes/registry.py`
- Create: `sweets/modes/clock.py`
- Create: `tests/modes/__init__.py`
- Create: `tests/modes/test_clock.py`

- [ ] **Step 1: Create mode base class**

Create `sweets/modes/__init__.py`:
```python
"""Mode framework for Vestaboard display modes."""

from sweets.modes.base import Mode
from sweets.modes.registry import get_all_modes, get_mode

__all__ = ["Mode", "get_all_modes", "get_mode"]
```

Create `sweets/modes/base.py`:
```python
"""Abstract base class for display modes."""

from abc import ABC, abstractmethod
from typing import Any

from sweets.core.board import Board


class Mode(ABC):
    """Base class for all display modes."""

    name: str = "Unknown"
    slug: str = "unknown"
    interval: int = 60  # seconds between updates

    def configure(self, settings: dict[str, Any]) -> None:
        """Apply mode-specific settings from config.

        Override in subclasses to handle settings.
        """
        pass

    @abstractmethod
    def render(self) -> Board:
        """Generate current board state.

        Returns:
            Board with the current display content
        """
        pass
```

- [ ] **Step 2: Create mode registry**

Create `sweets/modes/registry.py`:
```python
"""Mode auto-discovery and registry."""

import importlib
import pkgutil
from typing import Type

from sweets.modes.base import Mode

_registry: dict[str, Type[Mode]] = {}


def _discover_modes() -> None:
    """Scan modes package for Mode subclasses."""
    import sweets.modes as modes_package

    for _, module_name, _ in pkgutil.iter_modules(modes_package.__path__):
        if module_name in ("base", "registry"):
            continue

        module = importlib.import_module(f"sweets.modes.{module_name}")

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, Mode)
                and attr is not Mode
            ):
                _registry[attr.slug] = attr


def get_all_modes() -> dict[str, Type[Mode]]:
    """Return all discovered modes as {slug: ModeClass}."""
    if not _registry:
        _discover_modes()
    return _registry.copy()


def get_mode(slug: str) -> Mode:
    """Instantiate a mode by slug.

    Raises:
        KeyError: If mode slug not found
    """
    if not _registry:
        _discover_modes()

    if slug not in _registry:
        raise KeyError(f"Unknown mode: {slug}")

    return _registry[slug]()
```

- [ ] **Step 3: Write failing clock mode test**

Create `tests/modes/__init__.py`:
```python
"""Tests for display modes."""
```

Create `tests/modes/test_clock.py`:
```python
"""Tests for clock mode."""

from sweets.core.board import Board
from sweets.modes.clock import ClockMode


def test_clock_render_returns_board():
    """ClockMode.render() should return a valid Board."""
    mode = ClockMode()
    board = mode.render()

    assert isinstance(board, Board)
    assert len(board.rows) == 6
    assert len(board.rows[0]) == 22
```

- [ ] **Step 4: Run test to verify it fails**

Run: `pytest tests/modes/test_clock.py::test_clock_render_returns_board -v`

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 5: Implement ClockMode**

Create `sweets/modes/clock.py`:
```python
"""Clock display mode."""

from datetime import datetime
from typing import Any

from sweets.core.board import Board
from sweets.modes.base import Mode


class ClockMode(Mode):
    """Display current time on the board."""

    name = "Clock"
    slug = "clock"
    interval = 60

    def __init__(self) -> None:
        self.format_12h = True
        self.show_seconds = False

    def configure(self, settings: dict[str, Any]) -> None:
        """Apply clock settings."""
        fmt = settings.get("format", "12h")
        self.format_12h = fmt == "12h"
        self.show_seconds = settings.get("show_seconds", False)

    def render(self) -> Board:
        """Generate board with current time."""
        now = datetime.now()

        if self.format_12h:
            if self.show_seconds:
                time_str = now.strftime("%I:%M:%S %p")
            else:
                time_str = now.strftime("%I:%M %p")
        else:
            if self.show_seconds:
                time_str = now.strftime("%H:%M:%S")
            else:
                time_str = now.strftime("%H:%M")

        # Remove leading zero from hour
        time_str = time_str.lstrip("0")

        board = Board()
        board.center_text(2, time_str)

        return board
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/modes/test_clock.py::test_clock_render_returns_board -v`

Expected: PASS

- [ ] **Step 7: Add test for 12h format**

Add to `tests/modes/test_clock.py`:
```python
from unittest.mock import patch
from datetime import datetime


def test_clock_12h_format():
    """ClockMode should show AM/PM in 12h format."""
    mode = ClockMode()
    mode.configure({"format": "12h"})

    # Mock datetime to return a known time
    mock_time = datetime(2026, 5, 22, 14, 30, 0)  # 2:30 PM

    with patch("sweets.modes.clock.datetime") as mock_dt:
        mock_dt.now.return_value = mock_time
        board = mode.render()

    # Find the row with content
    from sweets.core.characters import codes_to_text

    for row in board.rows:
        text = codes_to_text(row).strip()
        if text:
            assert "PM" in text or "AM" in text, f"Expected AM/PM, got: {text}"
            break
```

- [ ] **Step 8: Run test to verify it passes**

Run: `pytest tests/modes/test_clock.py::test_clock_12h_format -v`

Expected: PASS

- [ ] **Step 9: Add test for 24h format**

Add to `tests/modes/test_clock.py`:
```python
def test_clock_24h_format():
    """ClockMode should show 24h time without AM/PM."""
    mode = ClockMode()
    mode.configure({"format": "24h"})

    mock_time = datetime(2026, 5, 22, 14, 30, 0)  # 14:30

    with patch("sweets.modes.clock.datetime") as mock_dt:
        mock_dt.now.return_value = mock_time
        board = mode.render()

    from sweets.core.characters import codes_to_text

    for row in board.rows:
        text = codes_to_text(row).strip()
        if text:
            assert "PM" not in text and "AM" not in text
            assert "14" in text or "4" in text, f"Expected 24h time, got: {text}"
            break
```

- [ ] **Step 10: Run all clock tests**

Run: `pytest tests/modes/test_clock.py -v`

Expected: All tests PASS

- [ ] **Step 11: Test mode registry**

Run:
```bash
python -c "from sweets.modes import get_all_modes, get_mode; print(get_all_modes()); m = get_mode('clock'); print(f'Got: {m.name}')"
```

Expected: `{'clock': <class 'sweets.modes.clock.ClockMode'>}` and `Got: Clock`

- [ ] **Step 12: Commit**

```bash
git add sweets/modes/ tests/modes/
git commit -m "feat: mode framework with clock mode implementation"
```

---

## Task 7: Scheduler

**Files:**
- Create: `sweets/scheduler.py`

- [ ] **Step 1: Create scheduler**

Create `sweets/scheduler.py`:
```python
"""Mode scheduler for running active mode in background."""

import threading
import time
from datetime import datetime
from typing import Any

from sweets.core.api import VestaboardClient
from sweets.core.board import Board
from sweets.modes import get_mode, get_all_modes
from sweets.modes.base import Mode


class Scheduler:
    """Manages the single active mode and its update loop."""

    def __init__(self, client: VestaboardClient, mode_settings: dict[str, dict[str, Any]] | None = None) -> None:
        self.client = client
        self.mode_settings = mode_settings or {}
        self.active_mode: Mode | None = None
        self._running = False
        self._thread: threading.Thread | None = None
        self._last_update: datetime | None = None
        self._last_board: Board | None = None

    def start(self, mode_slug: str) -> None:
        """Activate a mode and begin background update loop."""
        self.stop()  # Stop any existing mode

        mode = get_mode(mode_slug)
        settings = self.mode_settings.get(mode_slug, {})
        mode.configure(settings)

        self.active_mode = mode
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        # Immediate first update
        self._update()

    def stop(self) -> None:
        """Stop the current mode."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
        self.active_mode = None

    def get_status(self) -> dict[str, Any]:
        """Return current mode status."""
        return {
            "active_mode": self.active_mode.slug if self.active_mode else None,
            "mode_name": self.active_mode.name if self.active_mode else None,
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "running": self._running,
            "available_modes": list(get_all_modes().keys()),
        }

    def get_last_board(self) -> Board | None:
        """Return the last rendered board."""
        return self._last_board

    def send_message(self, text: str) -> bool:
        """Send a one-off message (doesn't affect active mode)."""
        board = Board.from_text(text)
        self._last_board = board
        self._last_update = datetime.now()
        return self.client.write(board)

    def _update(self) -> None:
        """Render and send current mode's board."""
        if self.active_mode is None:
            return

        board = self.active_mode.render()
        self._last_board = board
        self._last_update = datetime.now()

        try:
            self.client.write(board)
        except Exception as e:
            # Log but don't crash the loop
            print(f"Error writing to board: {e}")

    def _run_loop(self) -> None:
        """Background loop that updates at mode's interval."""
        while self._running and self.active_mode is not None:
            time.sleep(self.active_mode.interval)
            if self._running and self.active_mode is not None:
                self._update()
```

- [ ] **Step 2: Verify scheduler works**

Run:
```bash
python -c "
from sweets.scheduler import Scheduler
from sweets.core.api import CloudClient

# Create a mock that doesn't actually send
class MockClient(CloudClient):
    def write(self, board):
        print(f'Would write board with {sum(1 for r in board.rows for c in r if c != 0)} non-blank chars')
        return True

client = MockClient('fake-token')
scheduler = Scheduler(client)
scheduler.start('clock')
import time; time.sleep(0.1)
print(scheduler.get_status())
scheduler.stop()
"
```

Expected: Shows board write message and status with active_mode='clock'

- [ ] **Step 3: Commit**

```bash
git add sweets/scheduler.py
git commit -m "feat: scheduler for running modes in background thread"
```

---

## Task 8: Web UI

**Files:**
- Create: `sweets/web/__init__.py`
- Create: `sweets/web/app.py`
- Create: `sweets/web/templates/base.html`
- Create: `sweets/web/templates/index.html`

- [ ] **Step 1: Create web package**

Create `sweets/web/__init__.py`:
```python
"""Web UI for Vestaboard control."""
```

- [ ] **Step 2: Create Flask app**

Create `sweets/web/app.py`:
```python
"""Flask web application for Vestaboard control."""

from flask import Flask, render_template, request, redirect, url_for, jsonify

from sweets.config import load_config
from sweets.core.api import CloudClient, LocalClient
from sweets.scheduler import Scheduler
from sweets.modes import get_all_modes

app = Flask(__name__)

# Global scheduler instance (initialized in main)
scheduler: Scheduler | None = None


def get_scheduler() -> Scheduler:
    """Get or create the scheduler instance."""
    global scheduler
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized. Call main() first.")
    return scheduler


@app.route("/")
def index():
    """Dashboard homepage."""
    sched = get_scheduler()
    status = sched.get_status()
    modes = get_all_modes()

    # Get current board display
    board_display = None
    if sched.get_last_board() is not None:
        board_display = sched.get_last_board().to_array()

    return render_template(
        "index.html",
        status=status,
        modes=modes,
        board=board_display,
    )


@app.route("/status")
def status():
    """JSON status endpoint."""
    sched = get_scheduler()
    return jsonify(sched.get_status())


@app.route("/message", methods=["POST"])
def send_message():
    """Send a custom message to the board."""
    text = request.form.get("text", "").strip()
    if text:
        sched = get_scheduler()
        sched.send_message(text)
    return redirect(url_for("index"))


@app.route("/mode/<slug>", methods=["POST"])
def activate_mode(slug: str):
    """Switch to a different mode."""
    sched = get_scheduler()
    try:
        sched.start(slug)
    except KeyError:
        pass  # Invalid mode, just redirect
    return redirect(url_for("index"))


@app.route("/stop", methods=["POST"])
def stop_mode():
    """Stop the current mode."""
    sched = get_scheduler()
    sched.stop()
    return redirect(url_for("index"))


def main():
    """Entry point for the web application."""
    global scheduler

    config = load_config()

    # Create API client
    if config.api_type == "local":
        client = LocalClient(
            api_key=config.local_api_key or "",
            host=config.api_host,
        )
    else:
        client = CloudClient(api_token=config.cloud_api_token)

    # Create scheduler
    scheduler = Scheduler(client, mode_settings=config.modes)

    # Start default mode if configured
    if config.default_mode:
        try:
            scheduler.start(config.default_mode)
        except KeyError:
            pass

    # Run Flask
    app.run(host=config.web_host, port=config.web_port, debug=True)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Create base template**

Create directory and file:
```bash
mkdir -p sweets/web/templates
```

Create `sweets/web/templates/base.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sweets - Vestaboard Control</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        h1 {
            color: #fff;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }
        .board {
            display: grid;
            grid-template-columns: repeat(22, 1fr);
            gap: 3px;
            background: #000;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .cell {
            aspect-ratio: 1;
            background: #1a1a1a;
            border-radius: 3px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            color: #fff;
        }
        .cell.filled {
            background: #fff;
            color: #000;
        }
        .cell.color-63 { background: #ff0000; }
        .cell.color-64 { background: #ff8000; }
        .cell.color-65 { background: #ffff00; color: #000; }
        .cell.color-66 { background: #00ff00; color: #000; }
        .cell.color-67 { background: #0000ff; }
        .cell.color-68 { background: #8000ff; }
        .cell.color-69 { background: #ffffff; color: #000; }
        .cell.color-70 { background: #000000; }
        .section {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .section h2 {
            margin-top: 0;
            color: #fff;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            font-size: 16px;
            border: 1px solid #444;
            border-radius: 4px;
            background: #333;
            color: #fff;
            margin-bottom: 10px;
        }
        button, select {
            padding: 10px 20px;
            font-size: 14px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }
        button {
            background: #4a9eff;
            color: #fff;
        }
        button:hover {
            background: #3a8eef;
        }
        button.danger {
            background: #ff4a4a;
        }
        button.danger:hover {
            background: #ef3a3a;
        }
        select {
            background: #333;
            color: #fff;
            border: 1px solid #444;
        }
        .status {
            font-size: 14px;
            color: #aaa;
        }
        .status strong {
            color: #4a9eff;
        }
        .inline-form {
            display: flex;
            gap: 10px;
            align-items: center;
        }
    </style>
</head>
<body>
    <h1>Sweets</h1>
    {% block content %}{% endblock %}
</body>
</html>
```

- [ ] **Step 4: Create index template**

Create `sweets/web/templates/index.html`:
```html
{% extends "base.html" %}

{% block content %}
<div class="section">
    <h2>Board Preview</h2>
    <div class="board">
        {% if board %}
            {% for row in board %}
                {% for code in row %}
                    {% if code == 0 %}
                        <div class="cell"></div>
                    {% elif code >= 63 and code <= 70 %}
                        <div class="cell color-{{ code }}"></div>
                    {% elif code >= 1 and code <= 26 %}
                        <div class="cell filled">{{ "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[code - 1] }}</div>
                    {% elif code >= 27 and code <= 35 %}
                        <div class="cell filled">{{ code - 26 }}</div>
                    {% elif code == 36 %}
                        <div class="cell filled">0</div>
                    {% else %}
                        <div class="cell filled">?</div>
                    {% endif %}
                {% endfor %}
            {% endfor %}
        {% else %}
            {% for _ in range(6) %}
                {% for _ in range(22) %}
                    <div class="cell"></div>
                {% endfor %}
            {% endfor %}
        {% endif %}
    </div>
    <p class="status">
        <strong>Mode:</strong> {{ status.mode_name or "None" }}
        {% if status.last_update %}
        | <strong>Last update:</strong> {{ status.last_update }}
        {% endif %}
    </p>
</div>

<div class="section">
    <h2>Send Message</h2>
    <form action="{{ url_for('send_message') }}" method="post">
        <input type="text" name="text" placeholder="Type your message..." maxlength="132">
        <button type="submit">Send</button>
    </form>
</div>

<div class="section">
    <h2>Mode Control</h2>
    <div class="inline-form">
        <form action="{{ url_for('activate_mode', slug='') }}" method="post" id="mode-form">
            <select name="mode" onchange="this.form.action = '{{ url_for('activate_mode', slug='') }}' + this.value">
                <option value="">Select a mode...</option>
                {% for slug, mode_class in modes.items() %}
                    <option value="{{ slug }}" {% if status.active_mode == slug %}selected{% endif %}>
                        {{ mode_class.name }}
                    </option>
                {% endfor %}
            </select>
            <button type="submit">Activate</button>
        </form>
        <form action="{{ url_for('stop_mode') }}" method="post">
            <button type="submit" class="danger">Stop</button>
        </form>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Test web app starts**

Run:
```bash
python -c "
import sys
sys.path.insert(0, '.')
from sweets.web.app import app
print('Flask app created successfully')
print('Routes:', [rule.rule for rule in app.url_map.iter_rules()])
"
```

Expected: Shows Flask app created and lists routes including `/`, `/status`, `/message`, `/mode/<slug>`, `/stop`

- [ ] **Step 6: Commit**

```bash
git add sweets/web/
git commit -m "feat: Flask web UI with board preview and mode control"
```

---

## Task 9: TUI

**Files:**
- Create: `sweets/tui/__init__.py`
- Create: `sweets/tui/app.py`

- [ ] **Step 1: Create TUI package**

Create `sweets/tui/__init__.py`:
```python
"""Terminal UI for Vestaboard control."""
```

- [ ] **Step 2: Create Textual app**

Create `sweets/tui/app.py`:
```python
"""Textual TUI application for Vestaboard control."""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, Static, Select
from textual.binding import Binding

from sweets.config import load_config
from sweets.core.api import CloudClient, LocalClient
from sweets.core.characters import codes_to_text
from sweets.scheduler import Scheduler
from sweets.modes import get_all_modes


class BoardDisplay(Static):
    """Widget displaying the 6x22 Vestaboard grid."""

    def __init__(self) -> None:
        super().__init__()
        self._board: list[list[int]] | None = None

    def set_board(self, board: list[list[int]] | None) -> None:
        """Update the displayed board."""
        self._board = board
        self.refresh()

    def render(self) -> str:
        """Render the board as text."""
        if self._board is None:
            return "\n".join(["." * 22] * 6)

        lines = []
        for row in self._board:
            line = ""
            for code in row:
                if code == 0:
                    line += "."
                elif 1 <= code <= 26:
                    line += chr(64 + code)
                elif 27 <= code <= 35:
                    line += str(code - 26)
                elif code == 36:
                    line += "0"
                elif 63 <= code <= 70:
                    colors = ["R", "O", "Y", "G", "B", "V", "W", "K"]
                    line += colors[code - 63]
                else:
                    line += "?"
            lines.append(line)
        return "\n".join(lines)


class SweetsApp(App):
    """Textual application for Vestaboard control."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 2fr 1fr;
    }

    #board-container {
        height: 100%;
        border: solid green;
        padding: 1;
    }

    #controls {
        height: 100%;
        border: solid blue;
        padding: 1;
    }

    BoardDisplay {
        height: auto;
        padding: 1;
        background: $surface;
        text-style: bold;
        text-align: center;
    }

    #status {
        height: auto;
        padding: 1;
        margin-bottom: 1;
    }

    Input {
        margin-bottom: 1;
    }

    Button {
        margin: 1 0;
        width: 100%;
    }

    #stop-btn {
        background: red;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("m", "focus_mode", "Mode"),
        Binding("t", "focus_text", "Text"),
        Binding("s", "stop_mode", "Stop"),
    ]

    def __init__(self, scheduler: Scheduler) -> None:
        super().__init__()
        self.scheduler = scheduler

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="board-container"):
            yield Label("Board Preview", id="board-label")
            yield BoardDisplay()
            yield Label("", id="status")

        with Container(id="controls"):
            yield Label("Send Message")
            yield Input(placeholder="Type message...", id="message-input")
            yield Button("Send", id="send-btn", variant="primary")

            yield Label("Mode Control")
            modes = get_all_modes()
            options = [(mode_cls.name, slug) for slug, mode_cls in modes.items()]
            yield Select(options, id="mode-select", prompt="Select mode")
            yield Button("Activate", id="activate-btn", variant="success")
            yield Button("Stop", id="stop-btn", variant="error")

        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.update_display()
        self.set_interval(1, self.update_display)

    def update_display(self) -> None:
        """Update board display and status."""
        board_widget = self.query_one(BoardDisplay)
        status_label = self.query_one("#status", Label)

        last_board = self.scheduler.get_last_board()
        if last_board:
            board_widget.set_board(last_board.to_array())

        status = self.scheduler.get_status()
        mode_name = status.get("mode_name") or "None"
        last_update = status.get("last_update") or "Never"
        status_label.update(f"Mode: {mode_name} | Updated: {last_update}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "send-btn":
            input_widget = self.query_one("#message-input", Input)
            text = input_widget.value.strip()
            if text:
                self.scheduler.send_message(text)
                input_widget.value = ""
                self.update_display()

        elif event.button.id == "activate-btn":
            select = self.query_one("#mode-select", Select)
            if select.value and select.value != Select.BLANK:
                self.scheduler.start(str(select.value))
                self.update_display()

        elif event.button.id == "stop-btn":
            self.scheduler.stop()
            self.update_display()

    def action_focus_mode(self) -> None:
        """Focus the mode selector."""
        self.query_one("#mode-select").focus()

    def action_focus_text(self) -> None:
        """Focus the text input."""
        self.query_one("#message-input").focus()

    def action_stop_mode(self) -> None:
        """Stop the current mode."""
        self.scheduler.stop()
        self.update_display()


def main():
    """Entry point for the TUI application."""
    config = load_config()

    # Create API client
    if config.api_type == "local":
        client = LocalClient(
            api_key=config.local_api_key or "",
            host=config.api_host,
        )
    else:
        client = CloudClient(api_token=config.cloud_api_token)

    # Create scheduler
    scheduler = Scheduler(client, mode_settings=config.modes)

    # Start default mode if configured
    if config.default_mode:
        try:
            scheduler.start(config.default_mode)
        except KeyError:
            pass

    # Run app
    app = SweetsApp(scheduler)
    app.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Verify TUI imports work**

Run:
```bash
python -c "from sweets.tui.app import SweetsApp, main; print('TUI module imports successfully')"
```

Expected: `TUI module imports successfully`

- [ ] **Step 4: Commit**

```bash
git add sweets/tui/
git commit -m "feat: Textual TUI with board preview and mode control"
```

---

## Task 10: Final Integration and Testing

**Files:**
- Update: `tests/conftest.py`

- [ ] **Step 1: Update conftest with test config fixture**

Add to `tests/conftest.py`:
```python
from pathlib import Path
import tempfile

from sweets.config import Config


@pytest.fixture
def test_config() -> Config:
    """Config object with test values."""
    return Config(
        api_type="cloud",
        api_host="vestaboard.local",
        cloud_api_token="test-token",
        local_api_key=None,
        default_mode="clock",
        modes={"clock": {"format": "12h", "show_seconds": False}},
        web_host="127.0.0.1",
        web_port=5000,
    )


@pytest.fixture
def temp_config_files(tmp_path: Path):
    """Create temporary config files for testing."""
    config_path = tmp_path / "config.yaml"
    secrets_path = tmp_path / "secrets.yaml"

    config_path.write_text("""
api:
  type: cloud
default_mode: clock
modes:
  clock:
    format: 12h
""")

    secrets_path.write_text("""
cloud_api_token: test-token-123
""")

    return config_path, secrets_path
```

- [ ] **Step 2: Run full test suite**

Run: `pytest tests/ -v`

Expected: All tests PASS

- [ ] **Step 3: Verify entry points work**

Run:
```bash
python -c "
from sweets.web.app import main as web_main
from sweets.tui.app import main as tui_main
print('Entry points importable')
"
```

Expected: `Entry points importable`

- [ ] **Step 4: Final commit**

```bash
git add tests/conftest.py
git commit -m "feat: complete test fixtures and integration"
```

- [ ] **Step 5: Run final verification**

Run:
```bash
pytest tests/ -v --tb=short
```

Expected: All tests PASS

---

## Summary

After completing all tasks, the project will have:

1. **Core API layer** - Character encoding, board abstraction, Cloud API client
2. **Mode framework** - Plugin architecture with auto-discovery, clock mode
3. **Configuration** - YAML-based config with separated secrets
4. **Scheduler** - Background thread for mode updates
5. **Web UI** - Flask dashboard with board preview and controls
6. **TUI** - Textual terminal interface with same features
7. **Tests** - Unit tests for characters/board, integration tests for API

To run the web UI:
```bash
# First create secrets.yaml with your API token
cp secrets.yaml.example secrets.yaml
# Edit secrets.yaml with your token

# Then run
sweets-web
# or
python -m sweets.web.app
```

To run the TUI:
```bash
sweets-tui
# or
python -m sweets.tui.app
```
