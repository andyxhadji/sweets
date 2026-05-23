# Illustrations Mode Design

An illustrations mode for Vestaboard Note (3x15) that displays pixel-art style drawings and ASCII art using colored tiles.

## Overview

- **Target**: Vestaboard Note only (3x15 grid)
- **Illustrations**: 15 pre-defined designs across animals, nature, and symbols
- **Selection**: Manual via secondary dropdown that appears when mode is active
- **Rendering**: Combines colored tiles (codes 63-70), letters/symbols, and blanks

## Illustration Definitions

Each illustration is a 3x15 grid stored as a list of character codes:

```python
@dataclass
class Illustration:
    name: str
    grid: list[list[int]]  # 3 rows x 15 cols

ILLUSTRATIONS: dict[str, Illustration] = {
    "duck": Illustration(
        name="Duck",
        grid=[
            [0, 0, 65, 65, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 65, 65, 65, 65, 65, 65, 65, 65, 65, 0, 0, 0, 0, 0],
            [0, 0, 64, 64, 64, 64, 64, 64, 64, 0, 0, 0, 0, 0, 0],
        ]
    ),
    # ... 14 more
}
```

### Catalog

**Animals**: Duck, Cat, Dog, Fish, Bird

**Nature**: Sun, Moon, Tree, Flower, Cloud

**Symbols**: Heart, Star, Smiley, House, Car

## Mode Class

```python
class IllustrationsMode(Mode):
    name = "Illustrations"
    slug = "illustrations"
    interval = 3600

    def __init__(self, rows: int = 3, cols: int = 15) -> None:
        super().__init__(rows, cols)
        self.current = "duck"

    def configure(self, settings: dict) -> None:
        self.current = settings.get("default", "duck")

    def set_illustration(self, slug: str) -> None:
        if slug in ILLUSTRATIONS:
            self.current = slug

    def get_illustrations(self) -> list[tuple[str, str]]:
        return [(slug, ill.name) for slug, ill in ILLUSTRATIONS.items()]

    def render(self) -> Board:
        board = Board(rows=self.rows, cols=self.cols)
        illustration = ILLUSTRATIONS.get(self.current)
        if illustration:
            for row_idx, row_codes in enumerate(illustration.grid):
                board.set_row(row_idx, row_codes)
        return board
```

## UI Changes

### Web Interface

Secondary dropdown appears only when Illustrations mode is selected:

```html
<select name="illustration" id="illustration-select" style="display: none;">
  {% for slug, name in illustrations %}
    <option value="{{ slug }}">{{ name }}</option>
  {% endfor %}
</select>

<script>
modeSelect.addEventListener('change', function() {
  illustrationSelect.style.display =
    this.value === 'illustrations' ? 'inline' : 'none';
});
</script>
```

New endpoint to change illustration:

```python
@app.route("/illustration/<slug>", methods=["POST"])
def set_illustration(slug: str):
    sched = get_scheduler()
    mode = sched.get_active_mode()
    if hasattr(mode, 'set_illustration'):
        mode.set_illustration(slug)
        sched.force_update()
    return redirect(url_for("index"))
```

### TUI Interface

Secondary Select widget, shown/hidden based on mode selection:

```python
yield Select([], id="illustration-select")

def on_select_changed(self, event: Select.Changed) -> None:
    if event.select.id == "mode-select":
        ill_select = self.query_one("#illustration-select")
        if event.value == "illustrations":
            mode = get_mode("illustrations", self.board_rows, self.board_cols)
            ill_select.set_options(mode.get_illustrations())
            ill_select.display = True
        else:
            ill_select.display = False
```

## Scheduler Changes

Add methods to support illustration switching:

```python
def get_active_mode(self) -> Mode | None:
    """Return the currently running mode instance."""
    return self._active_mode

def force_update(self) -> None:
    """Force immediate re-render of current mode."""
    if self._active_mode:
        board = self._active_mode.render()
        self._send_board(board)
```

## Configuration

Optional config to set default illustration:

```yaml
modes:
  illustrations:
    default: sun
```

## Files to Create/Modify

| File | Action |
|------|--------|
| `sweets/modes/illustrations.py` | Create - mode class + illustration definitions |
| `tests/modes/test_illustrations.py` | Create - unit tests |
| `sweets/web/app.py` | Modify - add /illustration endpoint, pass data to template |
| `sweets/web/templates/index.html` | Modify - add secondary dropdown + JS |
| `sweets/tui/app.py` | Modify - add illustration Select + show/hide logic |
| `sweets/scheduler.py` | Modify - add force_update() and get_active_mode() |

## Testing

```python
def test_render_default_illustration():
    mode = IllustrationsMode(rows=3, cols=15)
    board = mode.render()
    assert board.to_array() == ILLUSTRATIONS["duck"].grid

def test_set_illustration():
    mode = IllustrationsMode(rows=3, cols=15)
    mode.set_illustration("sun")
    assert mode.current == "sun"

def test_set_invalid_illustration():
    mode = IllustrationsMode(rows=3, cols=15)
    mode.set_illustration("nonexistent")
    assert mode.current == "duck"

def test_get_illustrations():
    mode = IllustrationsMode(rows=3, cols=15)
    options = mode.get_illustrations()
    assert len(options) == 15

def test_configure_default():
    mode = IllustrationsMode(rows=3, cols=15)
    mode.configure({"default": "star"})
    assert mode.current == "star"
```
