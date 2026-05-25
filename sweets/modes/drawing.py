"""Drawing display mode for Vestaboard."""

from typing import Any

from sweets.core.board import Board
from sweets.modes.base import Mode


class DrawingMode(Mode):
    """Display a user-drawn grid on the board."""

    name = "Drawing"
    slug = "drawing"
    interval = None  # Static, no periodic updates

    def __init__(self, rows: int = 6, cols: int = 22) -> None:
        super().__init__(rows, cols)
        self.grid: list[list[int]] = []

    def configure(self, settings: dict[str, Any]) -> None:
        """Apply mode-specific settings from config."""
        self.grid = settings.get("grid", [])

    def render(self) -> Board:
        """Render the stored grid to the board."""
        board = Board(rows=self.rows, cols=self.cols)
        for i, row in enumerate(self.grid[: self.rows]):
            board.set_row(i, row[: self.cols])
        return board
