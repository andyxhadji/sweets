# Draw Mode Design

A dedicated page for creating pixel art on the Vestaboard by clicking and dragging on an interactive grid, then sending the result as a persistent mode.

## Overview

Users can draw on a grid representation of the Vestaboard using colors and characters, then send the result to the board. The drawing becomes an active "Drawing" mode that persists until the user switches to a different mode.

## User Flow

1. User clicks "Draw" link/button on main dashboard
2. User arrives at `/draw` page with empty grid and palette
3. User selects a brush (color or character) from the palette
4. User clicks or click-drags on cells to paint them
5. User clicks "Send" to push the drawing to the board
6. A new "Drawing" mode is started with the grid content
7. User is redirected to the main dashboard showing "Mode: Drawing"

## Page Layout

```
┌─────────────────────────────────────────────┐
│  Sweets - Draw Mode            [← Back]     │
├─────────────────────────────────────────────┤
│                                             │
│           ┌─────────────────┐               │
│           │                 │               │
│           │   Board Grid    │               │
│           │   (clickable)   │               │
│           │                 │               │
│           └─────────────────┘               │
│                                             │
│  ┌─ Palette ──────────────────────────────┐ │
│  │ [_] [R] [O] [Y] [G] [B] [V] [W] [K]    │ │
│  │ [A][B][C]...[Z] [0][1]...[9] [♥]       │ │
│  │                          Selected: [R]  │ │
│  └────────────────────────────────────────┘ │
│                                             │
│        [ Clear ]        [ Send ]            │
└─────────────────────────────────────────────┘
```

## Components

### Board Grid

- Renders as a CSS grid matching the configured board size (6x22 standard, 3x15 for Note)
- Each cell is clickable and displays its current content (blank, color, or character)
- Click on a cell fills it with the currently selected brush
- Click-and-drag paints multiple cells in one motion
- Hover state shows highlight to indicate the cell is interactive
- Reuses existing cell styling from `base.html` (color classes, filled state, etc.)

### Palette

**Row 1 - Colors:**
| Item | Code | Display |
|------|------|---------|
| Blank (eraser) | 0 | Empty cell |
| Red | 63 | Red square |
| Orange | 64 | Orange square |
| Yellow | 65 | Yellow square |
| Green | 66 | Green square |
| Blue | 67 | Blue square |
| Violet | 68 | Violet square |
| White | 69 | White square |
| Black | 70 | Black square |

**Row 2 - Characters:**
| Item | Codes | Display |
|------|-------|---------|
| A-Z | 1-26 | Letter buttons |
| 0-9 | 36, 27-35 | Number buttons |
| Heart | 62 | ♥ |

**Selection state:**
- Currently selected brush has a visible highlight (border or background change)
- Default selection: Blank (eraser)

### Actions

**Clear button:**
- Resets all cells to blank (code 0)
- No confirmation needed (easy to undo by redrawing)

**Send button:**
- Collects grid state as 2D array of character codes
- POSTs to `/draw/send` endpoint
- On success: starts Drawing mode, redirects to main dashboard
- On error (rate limit, quiet hours): shows flash message, stays on draw page

## Backend

### New Mode: DrawingMode

Location: `sweets/modes/drawing.py`

```python
class DrawingMode(Mode):
    name = "Drawing"
    slug = "drawing"
    interval = None  # Static, no updates

    def configure(self, settings: dict) -> None:
        self.grid = settings.get("grid", [])

    def render(self) -> Board:
        board = Board(rows=self.rows, cols=self.cols)
        for i, row in enumerate(self.grid[:self.rows]):
            board.set_row(i, row[:self.cols])
        return board
```

Key characteristics:
- `interval = None` means no periodic re-rendering
- Grid data passed via `settings["grid"]` when mode is started
- Renders exactly what the user drew

### Routes

**GET /draw**
- Renders `draw.html` template
- Passes `board_rows` and `board_cols` for grid sizing

**POST /draw/send**
- Accepts JSON body: `{"grid": [[int, ...], ...]}`
- Validates grid dimensions match board config
- Stores grid in scheduler's mode settings for "drawing"
- Starts the "drawing" mode
- Returns redirect to index (or JSON response for fetch-based submission)

### Template: draw.html

New template extending `base.html` with:
- Interactive grid (JavaScript handles click/drag)
- Palette UI
- Clear and Send buttons
- JavaScript for:
  - Tracking selected brush
  - Mouse event handling for click and drag
  - Grid state management
  - Form submission

## JavaScript Behavior

### State
```javascript
let selectedBrush = 0;  // Current brush (character code)
let grid = [];          // 2D array of character codes
let isDrawing = false;  // Whether mouse is held down
```

### Event Handlers

**Palette click:**
- Set `selectedBrush` to the clicked item's code
- Update visual selection indicator

**Cell mousedown / touchstart:**
- Set `isDrawing = true`
- Paint the cell with `selectedBrush`
- On touch: call `preventDefault()` to avoid scrolling

**Cell mouseenter / touchmove:**
- If `isDrawing`, paint the cell under the pointer/touch
- On touchmove: use `elementFromPoint()` to find the cell under the touch coordinates

**Document mouseup / touchend:**
- Set `isDrawing = false`

**Clear button:**
- Reset all `grid` values to 0
- Re-render all cells

**Send button:**
- POST grid to `/draw/send`
- Handle response (redirect or show error)

## Error Handling

- **Rate limit (409):** Flash message "Rate limited - please wait ~15 seconds", stay on page
- **Quiet hours (423):** Flash message "Vestaboard is in quiet hours", stay on page
- **Network error:** Flash message with error details

## Files to Create/Modify

### New Files
- `sweets/modes/drawing.py` — DrawingMode class
- `sweets/web/templates/draw.html` — Draw page template

### Modified Files
- `sweets/modes/__init__.py` — Register DrawingMode
- `sweets/web/app.py` — Add `/draw` and `/draw/send` routes
- `sweets/web/templates/index.html` — Add "Draw" navigation link

## Testing

- Unit test for DrawingMode render (given grid, produces correct Board)
- Test that `/draw/send` validates grid dimensions
- Test that sending starts the drawing mode
- Manual testing for click/drag interaction
