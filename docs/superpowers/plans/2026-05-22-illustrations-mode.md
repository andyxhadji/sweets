# Illustrations Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an Illustrations mode for Vestaboard Note (3x15) that displays pixel-art/ASCII drawings with a secondary dropdown for selecting illustrations.

**Architecture:** Single `IllustrationsMode` class holds 15 illustration definitions. Mode exposes `get_illustrations()` for UI dropdowns and `set_illustration(slug)` for switching. Scheduler gains `force_update()` to re-render on selection change. Web and TUI interfaces add conditional secondary dropdown.

**Tech Stack:** Python 3.11+, Flask, Textual, pytest

---

## File Structure

| File | Responsibility |
|------|----------------|
| `sweets/modes/illustrations.py` | Mode class + Illustration dataclass + 15 illustration grid definitions |
| `tests/modes/test_illustrations.py` | Unit tests for mode behavior |
| `sweets/scheduler.py` | Add `force_update()` method |
| `sweets/web/app.py` | Add `/illustration/<slug>` endpoint, pass illustrations to template |
| `sweets/web/templates/index.html` | Secondary dropdown with show/hide JS |
| `sweets/tui/app.py` | Secondary Select widget with show/hide logic |

---

### Task 1: Illustration Data Structure and Mode Class

**Files:**
- Create: `sweets/modes/illustrations.py`
- Test: `tests/modes/test_illustrations.py`

- [ ] **Step 1: Write failing test for default render**

```python
# tests/modes/test_illustrations.py
"""Tests for illustrations mode."""

import pytest

from sweets.modes.illustrations import IllustrationsMode, ILLUSTRATIONS


def test_render_default_illustration():
    """Mode renders duck by default."""
    mode = IllustrationsMode(rows=3, cols=15)
    board = mode.render()
    assert board.to_array() == ILLUSTRATIONS["duck"].grid
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/modes/test_illustrations.py::test_render_default_illustration -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'sweets.modes.illustrations'"

- [ ] **Step 3: Create illustrations module with Illustration dataclass and duck**

```python
# sweets/modes/illustrations.py
"""Illustrations display mode for Vestaboard Note."""

from dataclasses import dataclass

from sweets.core.board import Board
from sweets.modes.base import Mode


@dataclass
class Illustration:
    """A single illustration definition."""
    name: str
    grid: list[list[int]]  # 3 rows x 15 cols


# Color codes: 63=red, 64=orange, 65=yellow, 66=green, 67=blue, 68=violet, 69=white, 70=black
ILLUSTRATIONS: dict[str, Illustration] = {
    "duck": Illustration(
        name="Duck",
        grid=[
            [0, 0, 0, 0, 65, 65, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 65, 65, 65, 65, 65, 65, 65, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 64, 64, 64, 64, 64, 0, 0, 0, 0, 0, 0],
        ]
    ),
}


class IllustrationsMode(Mode):
    """Display pixel-art illustrations on the board."""

    name = "Illustrations"
    slug = "illustrations"
    interval = 3600

    def __init__(self, rows: int = 3, cols: int = 15) -> None:
        super().__init__(rows, cols)
        self.current = "duck"

    def render(self) -> Board:
        """Render the current illustration to the board."""
        board = Board(rows=self.rows, cols=self.cols)
        illustration = ILLUSTRATIONS.get(self.current)
        if illustration:
            for row_idx, row_codes in enumerate(illustration.grid):
                board.set_row(row_idx, row_codes)
        return board
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/modes/test_illustrations.py::test_render_default_illustration -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add sweets/modes/illustrations.py tests/modes/test_illustrations.py
git commit -m "feat(illustrations): add mode with duck illustration"
```

---

### Task 2: set_illustration and get_illustrations Methods

**Files:**
- Modify: `sweets/modes/illustrations.py`
- Test: `tests/modes/test_illustrations.py`

- [ ] **Step 1: Write failing tests for set/get methods**

Add to `tests/modes/test_illustrations.py`:

```python
def test_set_illustration():
    """Can switch between illustrations."""
    mode = IllustrationsMode(rows=3, cols=15)
    mode.set_illustration("duck")  # Only duck exists for now
    assert mode.current == "duck"


def test_set_invalid_illustration():
    """Invalid slug is ignored."""
    mode = IllustrationsMode(rows=3, cols=15)
    mode.set_illustration("nonexistent")
    assert mode.current == "duck"


def test_get_illustrations():
    """Returns all available illustrations."""
    mode = IllustrationsMode(rows=3, cols=15)
    options = mode.get_illustrations()
    assert ("duck", "Duck") in options
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/modes/test_illustrations.py -v`
Expected: FAIL with "AttributeError: 'IllustrationsMode' object has no attribute 'set_illustration'"

- [ ] **Step 3: Add set_illustration and get_illustrations methods**

Add to `IllustrationsMode` class in `sweets/modes/illustrations.py`:

```python
    def set_illustration(self, slug: str) -> None:
        """Change the current illustration."""
        if slug in ILLUSTRATIONS:
            self.current = slug

    def get_illustrations(self) -> list[tuple[str, str]]:
        """Return list of (slug, name) for UI dropdowns."""
        return [(slug, ill.name) for slug, ill in ILLUSTRATIONS.items()]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/modes/test_illustrations.py -v`
Expected: PASS (all 4 tests)

- [ ] **Step 5: Commit**

```bash
git add sweets/modes/illustrations.py tests/modes/test_illustrations.py
git commit -m "feat(illustrations): add set/get illustration methods"
```

---

### Task 3: Configure Method for Default Illustration

**Files:**
- Modify: `sweets/modes/illustrations.py`
- Test: `tests/modes/test_illustrations.py`

- [ ] **Step 1: Write failing test for configure**

Add to `tests/modes/test_illustrations.py`:

```python
def test_configure_default():
    """Config can set default illustration."""
    mode = IllustrationsMode(rows=3, cols=15)
    mode.configure({"default": "duck"})
    assert mode.current == "duck"


def test_configure_empty():
    """Empty config keeps default."""
    mode = IllustrationsMode(rows=3, cols=15)
    mode.configure({})
    assert mode.current == "duck"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/modes/test_illustrations.py::test_configure_default tests/modes/test_illustrations.py::test_configure_empty -v`
Expected: FAIL (configure doesn't change current)

- [ ] **Step 3: Add configure method**

Add to `IllustrationsMode` class in `sweets/modes/illustrations.py`:

```python
    def configure(self, settings: dict) -> None:
        """Apply mode-specific settings from config."""
        default = settings.get("default", "duck")
        if default in ILLUSTRATIONS:
            self.current = default
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/modes/test_illustrations.py -v`
Expected: PASS (all 6 tests)

- [ ] **Step 5: Commit**

```bash
git add sweets/modes/illustrations.py tests/modes/test_illustrations.py
git commit -m "feat(illustrations): add configure method for default"
```

---

### Task 4: Add All 15 Illustrations

**Files:**
- Modify: `sweets/modes/illustrations.py`
- Test: `tests/modes/test_illustrations.py`

- [ ] **Step 1: Write test for illustration count and validity**

Add to `tests/modes/test_illustrations.py`:

```python
def test_all_illustrations_valid():
    """All illustrations have valid 3x15 grids."""
    for slug, ill in ILLUSTRATIONS.items():
        assert len(ill.grid) == 3, f"{slug} should have 3 rows"
        for row in ill.grid:
            assert len(row) == 15, f"{slug} rows should have 15 cols"
            for code in row:
                assert 0 <= code <= 70, f"{slug} has invalid code {code}"


def test_illustration_count():
    """Should have 15 illustrations."""
    assert len(ILLUSTRATIONS) == 15
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/modes/test_illustrations.py::test_illustration_count -v`
Expected: FAIL with "assert 1 == 15"

- [ ] **Step 3: Add remaining 14 illustrations**

Replace the `ILLUSTRATIONS` dict in `sweets/modes/illustrations.py`:

```python
# Color codes: 63=red, 64=orange, 65=yellow, 66=green, 67=blue, 68=violet, 69=white, 70=black
# Letter codes: 1-26 = A-Z
ILLUSTRATIONS: dict[str, Illustration] = {
    # Animals
    "duck": Illustration(
        name="Duck",
        grid=[
            [0, 0, 0, 0, 65, 65, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 65, 65, 65, 65, 65, 65, 65, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 64, 64, 64, 64, 64, 0, 0, 0, 0, 0, 0],
        ]
    ),
    "cat": Illustration(
        name="Cat",
        grid=[
            [0, 68, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 68, 0],
            [0, 0, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 68, 0, 0, 0, 0, 0, 0, 0],
        ]
    ),
    "dog": Illustration(
        name="Dog",
        grid=[
            [64, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 64],
            [0, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 0],
            [0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 0, 0, 0, 0],
        ]
    ),
    "fish": Illustration(
        name="Fish",
        grid=[
            [0, 0, 0, 0, 67, 67, 67, 67, 67, 0, 0, 0, 0, 0, 0],
            [0, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 0, 0, 0],
            [0, 0, 0, 0, 67, 67, 67, 67, 67, 0, 0, 0, 0, 0, 0],
        ]
    ),
    "bird": Illustration(
        name="Bird",
        grid=[
            [0, 0, 0, 0, 0, 67, 67, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 67, 67, 67, 67, 67, 67, 67, 67, 67, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
    ),
    # Nature
    "sun": Illustration(
        name="Sun",
        grid=[
            [0, 0, 0, 65, 0, 65, 65, 65, 0, 65, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 65, 65, 65, 65, 65, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 65, 0, 65, 65, 65, 0, 65, 0, 0, 0, 0, 0],
        ]
    ),
    "moon": Illustration(
        name="Moon",
        grid=[
            [0, 0, 0, 0, 0, 69, 69, 69, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 69, 69, 0, 69, 69, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 69, 69, 69, 0, 0, 0, 0, 0, 0, 0],
        ]
    ),
    "tree": Illustration(
        name="Tree",
        grid=[
            [0, 0, 0, 0, 0, 66, 66, 66, 66, 66, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 66, 66, 66, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 0, 0, 0, 0],
        ]
    ),
    "flower": Illustration(
        name="Flower",
        grid=[
            [0, 0, 0, 0, 63, 0, 65, 0, 63, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 65, 63, 65, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 66, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
    ),
    "cloud": Illustration(
        name="Cloud",
        grid=[
            [0, 0, 0, 69, 69, 69, 69, 69, 69, 69, 0, 0, 0, 0, 0],
            [0, 0, 69, 69, 69, 69, 69, 69, 69, 69, 69, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
    ),
    # Symbols
    "heart": Illustration(
        name="Heart",
        grid=[
            [0, 0, 63, 63, 0, 0, 0, 63, 63, 0, 0, 0, 0, 0, 0],
            [0, 0, 63, 63, 63, 63, 63, 63, 63, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 63, 63, 63, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
    ),
    "star": Illustration(
        name="Star",
        grid=[
            [0, 0, 0, 0, 0, 0, 65, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 65, 65, 65, 65, 65, 65, 65, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 65, 0, 0, 0, 65, 0, 0, 0, 0, 0, 0],
        ]
    ),
    "smiley": Illustration(
        name="Smiley",
        grid=[
            [0, 0, 0, 0, 65, 0, 0, 0, 65, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 65, 0, 0, 0, 0, 0, 65, 0, 0, 0, 0, 0],
        ]
    ),
    "house": Illustration(
        name="House",
        grid=[
            [0, 0, 0, 0, 0, 63, 63, 63, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 63, 63, 63, 63, 63, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 63, 63, 70, 63, 63, 0, 0, 0, 0, 0, 0],
        ]
    ),
    "car": Illustration(
        name="Car",
        grid=[
            [0, 0, 0, 0, 63, 63, 63, 63, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 63, 63, 63, 63, 63, 63, 63, 63, 0, 0, 0, 0, 0],
            [0, 0, 0, 70, 0, 0, 0, 0, 70, 0, 0, 0, 0, 0, 0],
        ]
    ),
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/modes/test_illustrations.py -v`
Expected: PASS (all 8 tests)

- [ ] **Step 5: Commit**

```bash
git add sweets/modes/illustrations.py tests/modes/test_illustrations.py
git commit -m "feat(illustrations): add all 15 illustrations"
```

---

### Task 5: Add force_update to Scheduler

**Files:**
- Modify: `sweets/scheduler.py`
- Test: `tests/test_scheduler.py` (create if needed)

- [ ] **Step 1: Write failing test for force_update**

Create `tests/test_scheduler.py`:

```python
"""Tests for scheduler."""

from unittest.mock import MagicMock

from sweets.scheduler import Scheduler


def test_force_update_renders_and_sends():
    """force_update re-renders active mode and sends to board."""
    client = MagicMock()
    client.write.return_value = True
    scheduler = Scheduler(client, board_rows=3, board_cols=15)

    scheduler.start("clock")
    initial_board = scheduler.get_last_board()

    scheduler.force_update()

    assert scheduler.get_last_board() is not None
    assert client.write.called


def test_force_update_no_active_mode():
    """force_update does nothing if no active mode."""
    client = MagicMock()
    scheduler = Scheduler(client, board_rows=3, board_cols=15)

    scheduler.force_update()  # Should not raise

    assert not client.write.called
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_scheduler.py -v`
Expected: FAIL with "AttributeError: 'Scheduler' object has no attribute 'force_update'"

- [ ] **Step 3: Add force_update method to Scheduler**

Add to `Scheduler` class in `sweets/scheduler.py` after `_update` method:

```python
    def force_update(self) -> None:
        """Force immediate re-render of current mode."""
        if self.active_mode is not None:
            self._update()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_scheduler.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add sweets/scheduler.py tests/test_scheduler.py
git commit -m "feat(scheduler): add force_update method"
```

---

### Task 6: Web Interface - Pass Illustrations to Template

**Files:**
- Modify: `sweets/web/app.py`

- [ ] **Step 1: Read current web/app.py to understand structure**

The index route needs to pass illustrations data. We need to import from illustrations mode.

- [ ] **Step 2: Update index route to pass illustrations**

Modify the `index()` function in `sweets/web/app.py`:

Add import at top:
```python
from sweets.modes.illustrations import IllustrationsMode, ILLUSTRATIONS
```

Update the `index()` function to pass illustrations:
```python
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

    # Get illustrations for dropdown
    illustrations = [(slug, ill.name) for slug, ill in ILLUSTRATIONS.items()]

    # Get current illustration if in illustrations mode
    current_illustration = None
    if sched.active_mode and sched.active_mode.slug == "illustrations":
        current_illustration = sched.active_mode.current

    return render_template(
        "index.html",
        status=status,
        modes=modes,
        board=board_display,
        board_rows=sched.board_rows,
        board_cols=sched.board_cols,
        illustrations=illustrations,
        current_illustration=current_illustration,
    )
```

- [ ] **Step 3: Run existing tests to verify no regression**

Run: `pytest tests/test_api.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add sweets/web/app.py
git commit -m "feat(web): pass illustrations data to template"
```

---

### Task 7: Web Interface - Add Illustration Endpoint

**Files:**
- Modify: `sweets/web/app.py`

- [ ] **Step 1: Add /illustration/<slug> endpoint**

Add after the `activate_mode` route in `sweets/web/app.py`:

```python
@app.route("/illustration/<slug>", methods=["POST"])
def set_illustration(slug: str):
    """Change the current illustration."""
    sched = get_scheduler()
    if sched.active_mode and hasattr(sched.active_mode, "set_illustration"):
        sched.active_mode.set_illustration(slug)
        sched.force_update()
    return redirect(url_for("index"))
```

- [ ] **Step 2: Run app to verify endpoint works**

Run: `python -c "from sweets.web.app import app; print('Import OK')"`
Expected: "Import OK"

- [ ] **Step 3: Commit**

```bash
git add sweets/web/app.py
git commit -m "feat(web): add illustration selection endpoint"
```

---

### Task 8: Web Interface - Secondary Dropdown in Template

**Files:**
- Modify: `sweets/web/templates/index.html`

- [ ] **Step 1: Add secondary dropdown and JavaScript**

Replace the Mode Control section in `sweets/web/templates/index.html`:

```html
<div class="section">
    <h2>Mode Control</h2>
    <div class="inline-form">
        <form action="{{ url_for('activate_mode', slug='') }}" method="post" id="mode-form">
            <select name="mode" id="mode-select" onchange="this.form.action = '{{ url_for('activate_mode', slug='') }}' + this.value; updateIllustrationVisibility();">
                <option value="">Select a mode...</option>
                {% for slug, mode_class in modes.items() %}
                    <option value="{{ slug }}" {% if status.active_mode == slug %}selected{% endif %}>
                        {{ mode_class.name }}
                    </option>
                {% endfor %}
            </select>
            <button type="submit">Activate</button>
        </form>
        <form action="{{ url_for('set_illustration', slug='') }}" method="post" id="illustration-form" style="display: none;">
            <select name="illustration" id="illustration-select" onchange="this.form.action = '{{ url_for('set_illustration', slug='') }}' + this.value;">
                {% for slug, name in illustrations %}
                    <option value="{{ slug }}" {% if current_illustration == slug %}selected{% endif %}>
                        {{ name }}
                    </option>
                {% endfor %}
            </select>
            <button type="submit">Set</button>
        </form>
        <form action="{{ url_for('stop_mode') }}" method="post">
            <button type="submit" class="danger">Stop</button>
        </form>
    </div>
</div>

<script>
function updateIllustrationVisibility() {
    var modeSelect = document.getElementById('mode-select');
    var illustrationForm = document.getElementById('illustration-form');
    if (modeSelect.value === 'illustrations') {
        illustrationForm.style.display = 'inline';
    } else {
        illustrationForm.style.display = 'none';
    }
}
// Initialize on page load
updateIllustrationVisibility();
</script>
```

- [ ] **Step 2: Run web app and test manually**

Run: `cd /Users/andy/.superset/worktrees/8122df7f-7a5a-4e4e-bf8c-e8d3ace33992/boatneck-clef && python -m sweets.web.app`

Test:
1. Open http://127.0.0.1:5000
2. Select "Illustrations" from mode dropdown - secondary dropdown should appear
3. Select another mode - secondary dropdown should hide
4. Select "Illustrations" again and pick an illustration - should update

- [ ] **Step 3: Commit**

```bash
git add sweets/web/templates/index.html
git commit -m "feat(web): add secondary dropdown for illustration selection"
```

---

### Task 9: TUI Interface - Add Illustration Selector

**Files:**
- Modify: `sweets/tui/app.py`

- [ ] **Step 1: Add import for illustrations**

Add import at top of `sweets/tui/app.py`:
```python
from sweets.modes.illustrations import ILLUSTRATIONS
```

- [ ] **Step 2: Add illustration Select widget in compose method**

Update the `compose` method in `SweetsApp` class. Find this section:

```python
            yield Label("Mode Control")
            modes = get_all_modes()
            options = [(mode_cls.name, slug) for slug, mode_cls in modes.items()]
            yield Select(options, id="mode-select", prompt="Select mode")
            yield Button("Activate", id="activate-btn", variant="success")
            yield Button("Stop", id="stop-btn", variant="error")
```

Replace with:

```python
            yield Label("Mode Control")
            modes = get_all_modes()
            options = [(mode_cls.name, slug) for slug, mode_cls in modes.items()]
            yield Select(options, id="mode-select", prompt="Select mode")

            # Illustration selector (hidden by default)
            ill_options = [(ill.name, slug) for slug, ill in ILLUSTRATIONS.items()]
            yield Select(ill_options, id="illustration-select", prompt="Select illustration")

            yield Button("Activate", id="activate-btn", variant="success")
            yield Button("Stop", id="stop-btn", variant="error")
```

- [ ] **Step 3: Add CSS to hide illustration select by default**

Add to the `CSS` string in `SweetsApp`:

```python
    #illustration-select {
        display: none;
    }
```

- [ ] **Step 4: Add on_select_changed handler**

Add method to `SweetsApp` class:

```python
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select widget changes."""
        if event.select.id == "mode-select":
            ill_select = self.query_one("#illustration-select", Select)
            if event.value == "illustrations":
                ill_select.styles.display = "block"
            else:
                ill_select.styles.display = "none"
        elif event.select.id == "illustration-select":
            if self.scheduler.active_mode and hasattr(self.scheduler.active_mode, "set_illustration"):
                self.scheduler.active_mode.set_illustration(str(event.value))
                self.scheduler.force_update()
                self.update_display()
```

- [ ] **Step 5: Update on_button_pressed to show selector when activating illustrations**

Update the `activate-btn` handler in `on_button_pressed`:

```python
        elif event.button.id == "activate-btn":
            select = self.query_one("#mode-select", Select)
            if select.value and select.value != Select.BLANK:
                self.scheduler.start(str(select.value))
                # Show/hide illustration selector
                ill_select = self.query_one("#illustration-select", Select)
                if select.value == "illustrations":
                    ill_select.styles.display = "block"
                else:
                    ill_select.styles.display = "none"
                self.update_display()
```

- [ ] **Step 6: Run TUI to test**

Run: `cd /Users/andy/.superset/worktrees/8122df7f-7a5a-4e4e-bf8c-e8d3ace33992/boatneck-clef && python -m sweets.tui.app`

Test:
1. Select "Illustrations" mode and activate
2. Illustration dropdown should appear
3. Select different illustrations - board should update

- [ ] **Step 7: Commit**

```bash
git add sweets/tui/app.py
git commit -m "feat(tui): add secondary dropdown for illustration selection"
```

---

### Task 10: Final Integration Test

**Files:**
- Test all components together

- [ ] **Step 1: Run all tests**

Run: `pytest -v`
Expected: All tests pass

- [ ] **Step 2: Test web interface end-to-end**

Run: `python -m sweets.web.app`

Verify:
1. Illustrations mode appears in dropdown
2. Secondary dropdown shows/hides correctly
3. Selecting illustrations updates the board preview

- [ ] **Step 3: Test TUI end-to-end**

Run: `python -m sweets.tui.app`

Verify:
1. Illustrations mode appears in dropdown
2. Secondary dropdown shows/hides correctly
3. Selecting illustrations updates the board display

- [ ] **Step 4: Final commit if any fixes needed**

```bash
git status
# If clean, skip. Otherwise:
git add -A
git commit -m "fix: integration fixes for illustrations mode"
```
