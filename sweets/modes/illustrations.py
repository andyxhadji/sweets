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
