# Vestaboard Platform Design

A Python platform for controlling Vestaboard displays with a modular mode architecture, web UI, and terminal UI.

## Overview

**Goals:**
- Python wrappers over Vestaboard Cloud API (Local API support later)
- Modular "modes" system where one mode is active at a time
- Web UI (Flask) for browser-based control
- TUI (Textual) for terminal-based control
- File-based configuration with secrets separated

**Initial scope:** Clock mode only, with architecture supporting easy addition of future modes.

## Architecture

### Core API Layer

#### `sweets/core/characters.py` - Character Encoding

Maps characters to Vestaboard integer codes per the official spec.

| Range | Characters | Codes |
|-------|-----------|-------|
| Letters | A-Z | 1-26 |
| Digits | 1-9, 0 | 27-36 |
| Punctuation | ! @ # $ ( ) - + & = ; : ' " % , . / ? | 37-60 |
| Special | degree/heart | 62 |
| Colors | red, orange, yellow, green, blue, violet, white, black | 63-70 |
| Blank | (empty) | 0 |

Functions:
- `CHAR_MAP: dict[str, int]` - Character to code mapping
- `text_to_codes(text: str) -> list[int]` - Convert text to codes, unsupported chars become 0
- `codes_to_text(codes: list[int]) -> str` - Convert codes back to text

#### `sweets/core/board.py` - Board Abstraction

Represents the 6 row x 22 column Vestaboard grid.

```python
class Board:
    rows: list[list[int]]  # 6 rows of 22 integers

    @classmethod
    def from_text(cls, message: str) -> "Board":
        """Parse text with word wrapping and centering."""

    def to_array(self) -> list[list[int]]:
        """Return API-ready 6x22 nested list."""

    def set_row(self, index: int, codes: list[int]) -> None:
        """Set a specific row."""

    def center_text(self, row: int, text: str) -> None:
        """Center text on a row."""

    def clear(self) -> None:
        """Reset all cells to blank (0)."""
```

#### `sweets/core/api.py` - Vestaboard Client

Abstract client with Cloud implementation (Local stubbed for later).

```python
class VestaboardClient(ABC):
    @abstractmethod
    def read(self) -> Board:
        """Get current board state."""

    @abstractmethod
    def write(self, board: Board) -> bool:
        """Send board state, return success."""

class CloudClient(VestaboardClient):
    """Cloud API at https://cloud.vestaboard.com"""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://cloud.vestaboard.com"

    # Headers: X-Vestaboard-Token, Content-Type: application/json
    # GET / - read current message
    # POST / - write message (body: {"characters": [[...], ...]})

class LocalClient(VestaboardClient):
    """Local API at http://vestaboard.local:7000 (stubbed)"""
    pass

def get_client(config: Config) -> VestaboardClient:
    """Factory function based on config.api.type"""
```

### Mode Framework

#### `sweets/modes/base.py` - Abstract Base Class

```python
class Mode(ABC):
    name: str       # Display name, e.g. "Clock"
    slug: str       # Identifier, e.g. "clock"
    interval: int   # Seconds between updates, default 60

    @abstractmethod
    def render(self) -> Board:
        """Generate current board state."""

    def configure(self, settings: dict) -> None:
        """Apply mode-specific settings from config."""
```

#### `sweets/modes/registry.py` - Auto-Discovery

Scans the `modes/` directory for `Mode` subclasses.

```python
def get_all_modes() -> dict[str, type[Mode]]:
    """Return {slug: ModeClass} for all discovered modes."""

def get_mode(slug: str) -> Mode:
    """Instantiate a mode by slug."""
```

#### `sweets/modes/clock.py` - Clock Mode

Displays current time centered on the board.

Settings:
- `format`: "12h" or "24h" (default: "12h")
- `show_seconds`: bool (default: false)

Updates every 60 seconds by default.

### Scheduler

#### `sweets/scheduler.py` - Mode Runner

Manages the single active mode and its update loop.

```python
class Scheduler:
    def __init__(self, client: VestaboardClient):
        self.client = client
        self.active_mode: Mode | None = None
        self._running: bool = False

    def start(self, mode_slug: str) -> None:
        """Activate a mode, begin background update loop."""

    def stop(self) -> None:
        """Stop the current mode."""

    def get_status(self) -> dict:
        """Return current mode, last update, next update time."""
```

Runs in a background thread, calls `mode.render()` at the configured interval, sends to board via client.

### Configuration

#### `config.yaml` - Main Config (committed)

```yaml
api:
  type: cloud  # "cloud" or "local"
  host: vestaboard.local  # for local API

default_mode: clock

modes:
  clock:
    format: 12h
    show_seconds: false

web:
  host: 127.0.0.1
  port: 5000
```

#### `secrets.yaml` - Secrets (gitignored)

```yaml
cloud_api_token: "your-token-here"
local_api_key: "your-key-here"
```

#### `sweets/config.py` - Loader

```python
@dataclass
class Config:
    api_type: str
    api_host: str
    cloud_api_token: str
    local_api_key: str | None
    default_mode: str
    modes: dict[str, dict]
    web_host: str
    web_port: int

def load_config() -> Config:
    """Load config.yaml + secrets.yaml, validate, return Config."""
```

### Web UI

#### `sweets/web/app.py` - Flask Application

Routes:
- `GET /` - Dashboard homepage
- `GET /status` - JSON: current mode and board state
- `POST /message` - Send custom message (form: `text`)
- `POST /mode/<slug>` - Switch to mode
- `POST /stop` - Stop current mode

#### Templates

`sweets/web/templates/base.html` - Layout with navigation and styles

`sweets/web/templates/index.html` - Dashboard:
- Board preview: 6x22 grid styled like Vestaboard
- Mode selector: dropdown + Activate button
- Message input: text field + Send button
- Status: active mode, last update time

Minimal CSS, either inline or `static/style.css`.

### TUI

#### `sweets/tui/app.py` - Textual Application

Three-panel layout:
1. **Board Preview** - Styled 6x22 grid
2. **Mode Control** - List of modes, select to switch
3. **Message Input** - Text field for custom messages

Status bar: active mode, last update, connection status

Key bindings:
- `q` - Quit
- `m` - Focus mode selector
- `t` - Focus text input
- `Enter` - Activate/send
- `s` - Stop mode

#### `sweets/tui/widgets.py` (optional)

Custom `BoardDisplay` widget for rendering the grid with colors.

## Project Structure

```
sweets/
├── config.yaml
├── secrets.yaml              # gitignored
├── pyproject.toml
├── README.md
├── .gitignore
├── sweets/
│   ├── __init__.py
│   ├── config.py
│   ├── scheduler.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── board.py
│   │   └── characters.py
│   ├── modes/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── registry.py
│   │   └── clock.py
│   ├── web/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   └── templates/
│   │       ├── base.html
│   │       └── index.html
│   └── tui/
│       ├── __init__.py
│       └── app.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_characters.py
    ├── test_board.py
    ├── test_api.py
    └── modes/
        ├── __init__.py
        └── test_clock.py
```

## Dependencies

```toml
[project]
dependencies = [
    "requests",
    "pyyaml",
    "flask",
    "textual",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "responses",
]

[project.scripts]
sweets-web = "sweets.web.app:main"
sweets-tui = "sweets.tui.app:main"
```

## Testing Strategy

### Unit Tests

**`tests/test_characters.py`**
- `test_text_to_codes_letters` - A-Z map to 1-26
- `test_text_to_codes_digits` - 0-9 map correctly
- `test_text_to_codes_punctuation` - Special chars map correctly
- `test_text_to_codes_unsupported` - Unknown chars become 0
- `test_codes_to_text_roundtrip` - Encode/decode preserves text

**`tests/test_board.py`**
- `test_board_dimensions` - Always 6x22
- `test_from_text_simple` - Short text centered
- `test_from_text_wrapping` - Long text wraps
- `test_to_array_format` - Correct nested list structure

**`tests/modes/test_clock.py`**
- `test_clock_render_returns_board` - Returns valid Board
- `test_clock_12h_format` - AM/PM format works
- `test_clock_24h_format` - 24h format works

### Integration Tests

**`tests/test_api.py`** - Using `responses` library to mock HTTP

- `test_cloud_client_read` - GET returns Board
- `test_cloud_client_write` - POST sends correct payload
- `test_cloud_client_auth_header` - Token in headers
- `test_cloud_client_error_handling` - Handles 401, 500, network errors

### Fixtures (`tests/conftest.py`)

- `mock_cloud_api` - responses mock for cloud.vestaboard.com
- `sample_board` - Pre-populated Board
- `test_config` - Config with test values

## Entry Points

| Command | Description |
|---------|-------------|
| `sweets-web` | Start Flask web server |
| `sweets-tui` | Start Textual TUI |
| `python -m sweets.web.app` | Alternative web start |
| `python -m sweets.tui.app` | Alternative TUI start |

## Future Modes (not in initial scope)

Examples of modes that can be added later:
- **Sweet Messages** - Rotate through affirmations from a list
- **MTA Train Times** - Show subway arrival times via MTA API
- **Weather** - Current temperature and conditions
- **Manual** - Display last message sent via UI (no auto-updates)

Adding a mode requires:
1. Create `sweets/modes/mymode.py`
2. Define class extending `Mode`
3. Implement `render()` method
4. Optionally add settings to `config.yaml` under `modes.mymode`

The registry auto-discovers it.
