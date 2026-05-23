"""Board abstraction for Vestaboard displays."""

from sweets.core.characters import text_to_codes, codes_to_text

# Default dimensions (standard Vestaboard)
DEFAULT_ROWS = 6
DEFAULT_COLS = 22


class Board:
    """Represents a Vestaboard character grid."""

    def __init__(self, rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS) -> None:
        """Initialize an empty board (all blanks)."""
        self.num_rows = rows
        self.num_cols = cols
        self.rows: list[list[int]] = [[0] * self.num_cols for _ in range(self.num_rows)]

    def to_array(self) -> list[list[int]]:
        """Return API-ready nested list."""
        return [row[:] for row in self.rows]

    def clear(self) -> None:
        """Reset all cells to blank (0)."""
        self.rows = [[0] * self.num_cols for _ in range(self.num_rows)]

    def set_row(self, index: int, codes: list[int]) -> None:
        """Set a specific row, padding or truncating to fit."""
        if index < 0 or index >= self.num_rows:
            raise IndexError(f"Row index must be 0-{self.num_rows - 1}")
        # Pad with zeros if too short, truncate if too long
        padded = (codes + [0] * self.num_cols)[:self.num_cols]
        self.rows[index] = padded

    def center_text(self, row: int, text: str) -> None:
        """Center text on a row."""
        codes = text_to_codes(text)
        if len(codes) >= self.num_cols:
            self.set_row(row, codes[:self.num_cols])
            return
        padding = (self.num_cols - len(codes)) // 2
        centered = [0] * padding + codes + [0] * (self.num_cols - padding - len(codes))
        self.set_row(row, centered)

    @classmethod
    def from_text(cls, message: str, rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS) -> "Board":
        """Create a board from text with word wrapping and centering."""
        board = cls(rows=rows, cols=cols)
        words = message.split()

        if not words:
            return board

        def display_len(s: str) -> int:
            """Calculate display length, treating {token} as 1 character."""
            import re
            # Remove {token} patterns and count as 1 each
            tokens = re.findall(r'\{[^}]+\}', s)
            base = re.sub(r'\{[^}]+\}', '', s)
            return len(base) + len(tokens)

        # Build lines that fit within cols
        lines: list[str] = []
        current_line = ""

        for word in words:
            if not current_line:
                current_line = word
            elif display_len(current_line) + 1 + display_len(word) <= cols:
                current_line += " " + word
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # Center lines vertically
        start_row = max(0, (rows - len(lines)) // 2)

        for i, line in enumerate(lines[:rows]):
            board.center_text(start_row + i, line)

        return board
