# CLAUDE.md

## Project Overview

**sweets** is a Python platform for controlling Vestaboard displays. It provides a scheduler, display modes, and multiple interfaces (TUI and web) for managing boards.

## Quick Reference

```bash
# Install
pip install -e ".[dev]"

# Run tests
pytest

# Run web interface
sweets-web

# Run terminal UI
sweets-tui
```

## Architecture

```
sweets/
├── core/           # Board abstraction, API clients, character encoding
├── modes/          # Display modes (clock, drawing, illustrations, reflections)
├── tui/            # Textual terminal interface
├── web/            # Flask web interface
├── config.py       # YAML config loading
└── scheduler.py    # Background mode runner
```

### Key Concepts

- **Board**: 2D grid of character codes (6x22 standard, 3x15 for Note)
- **Mode**: Abstract class with `render() -> Board` method and configurable interval
- **VestaboardClient**: Abstract API client (CloudClient implemented, LocalClient stubbed)

## Development Guidelines

### Testing

- Run all tests: `pytest`
- Run specific test file: `pytest tests/test_board.py`
- Run with verbose output: `pytest -v`

Tests use:
- `pytest` for test framework
- `responses` library for mocking HTTP requests to Vestaboard API
- Fixtures defined in `tests/conftest.py` (`sample_board`, `mock_cloud_api`, `test_config`)

### Code Style

- Python 3.11+ required
- Type hints on all function signatures
- Docstrings on classes and public methods
- Use `list[...]` and `dict[...]` (not `List`/`Dict` from typing)

### Adding a New Mode

1. Create `sweets/modes/your_mode.py` extending `Mode` base class
2. Implement required class attributes: `name`, `slug`, `interval`
3. Implement `render() -> Board` method
4. Optionally override `configure(settings: dict)` for config support
5. Register in `sweets/modes/__init__.py`
6. Add tests in `tests/modes/test_your_mode.py`

### Configuration

- `config.yaml`: Board dimensions, API type, mode settings, web server config
- `secrets.yaml`: API tokens (gitignored, see `secrets.yaml.example`)

## Character Encoding

Vestaboard uses numeric codes:
- 0: Blank
- 1-26: A-Z
- 27-36: 1-9, 0
- 37-60: Punctuation
- 63-70: Colors (red, orange, yellow, green, blue, violet, white, black)

Use `{red}`, `{heart}`, `{green}` tokens in text for special characters.

## Common Patterns

### Creating a Board with Text
```python
from sweets.core.board import Board
board = Board.from_text("HELLO WORLD")  # Auto word-wrap and center
```

### Mocking API in Tests
```python
def test_something(mock_cloud_api):
    mock_cloud_api.add(responses.GET, "https://cloud.vestaboard.com/", json={...})
    # test code
```
