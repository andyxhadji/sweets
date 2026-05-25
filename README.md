# sweets 🍬

A Python platform for controlling [Vestaboard](https://www.vestaboard.com/) displays. Provides a scheduler, display modes, and multiple interfaces (TUI and web) for managing your board.

## Features

- **Multi-board support** - Works with standard Vestaboard (6x22) and Vestaboard Note (3x15)
- **Cloud API integration** - Connect via Vestaboard's Cloud API
- **Local API ready** - Local API client stubbed for future implementation
- **Extensible mode system** - Add custom display modes with configurable intervals
- **Built-in Clock mode** - 12h/24h formats with optional seconds display
- **Terminal UI** - Textual-based TUI with live board preview and controls
- **Web interface** - Flask dashboard for browser-based control
- **Rate limit handling** - Automatic retry logic for API rate limits
- **Custom messages** - Send one-off text messages with word wrapping and centering
- **Color and icon support** - Use `{red}`, `{green}`, `{heart}` tokens in messages

## Installation

```bash
pip install -e .

# With dev dependencies
pip install -e ".[dev]"
```

Requires Python 3.11+.

## Configuration

Create `config.yaml` in your working directory:

```yaml
board:
  rows: 6    # 6 for standard, 3 for Note
  cols: 22   # 22 for standard, 15 for Note

api:
  type: cloud  # "cloud" only (local API not yet implemented)
  # host: vestaboard.local  # for future local API support

default_mode: clock

modes:
  clock:
    format: 12h  # or 24h
    show_seconds: false

web:
  host: 127.0.0.1
  port: 5000
```

Create `secrets.yaml` for API credentials:

```yaml
cloud_api_token: "your-token-here"
# local_api_key: "your-local-key"  # for future local API support
```

## Usage

### Terminal UI

```bash
sweets-tui
```

Keybindings:
- `q` - Quit
- `m` - Focus mode selector
- `t` - Focus text input
- `s` - Stop current mode

### Web Interface

```bash
sweets-web
```

Opens a Flask dashboard at http://127.0.0.1:5000 with:
- Live board preview
- Message sending
- Mode activation/control

## Architecture

```
sweets/
├── core/
│   ├── api.py        # Vestaboard API clients (Cloud, Local)
│   ├── board.py      # Board abstraction with text rendering
│   └── characters.py # Character encoding (A-Z, 0-9, colors, icons)
├── modes/
│   ├── base.py       # Abstract Mode class
│   ├── clock.py      # Clock display mode
│   └── registry.py   # Mode discovery and registration
├── tui/
│   └── app.py        # Textual terminal interface
├── web/
│   └── app.py        # Flask web interface
├── config.py         # YAML config loading
└── scheduler.py      # Background mode runner
```

## Creating Custom Modes

Extend the `Mode` base class:

```python
from sweets.core.board import Board
from sweets.modes.base import Mode

class WeatherMode(Mode):
    name = "Weather"
    slug = "weather"
    interval = 300  # update every 5 minutes

    def configure(self, settings: dict) -> None:
        self.location = settings.get("location", "NYC")

    def render(self) -> Board:
        board = Board(rows=self.rows, cols=self.cols)
        # Fetch weather and populate board
        board.center_text(2, "SUNNY 72F")
        return board
```

Register in `sweets/modes/__init__.py`.

## Character Encoding

Vestaboard uses numeric codes for characters:

| Range | Meaning |
|-------|---------|
| 0 | Blank |
| 1-26 | A-Z |
| 27-36 | 1-9, 0 |
| 37-60 | Punctuation |
| 62 | Degree/Heart icon |
| 63-70 | Colors (red, orange, yellow, green, blue, violet, white, black) |

Use special tokens in text: `{red}`, `{heart}`, `{green}`, etc.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT
