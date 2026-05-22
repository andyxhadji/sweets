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

    def set_row(self, index: int, codes: list[int]) -> None:
        """Set a specific row, padding or truncating to 22 chars."""
        if index < 0 or index >= ROWS:
            raise IndexError(f"Row index must be 0-{ROWS - 1}")
        # Pad with zeros if too short, truncate if too long
        padded = (codes + [0] * COLS)[:COLS]
        self.rows[index] = padded

    def center_text(self, row: int, text: str) -> None:
        """Center text on a row."""
        codes = text_to_codes(text)
        if len(codes) >= COLS:
            self.set_row(row, codes[:COLS])
            return
        padding = (COLS - len(codes)) // 2
        centered = [0] * padding + codes + [0] * (COLS - padding - len(codes))
        self.set_row(row, centered)

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
