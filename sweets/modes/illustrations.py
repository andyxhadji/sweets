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


class IllustrationsMode(Mode):
    """Display pixel-art illustrations on the board."""

    name = "Illustrations"
    slug = "illustrations"
    interval = 3600

    def __init__(self, rows: int = 3, cols: int = 15) -> None:
        super().__init__(rows, cols)
        self.current = "duck"

    def configure(self, settings: dict) -> None:
        """Apply mode-specific settings from config."""
        default = settings.get("default", "duck")
        if default in ILLUSTRATIONS:
            self.current = default
        # Also check for 'illustration' key (set by web/TUI when switching)
        illustration = settings.get("illustration")
        if illustration and illustration in ILLUSTRATIONS:
            self.current = illustration

    def render(self) -> Board:
        """Render the current illustration to the board.

        Illustrations are 3x15 (Note size). On larger boards, they are
        centered vertically and horizontally.
        """
        board = Board(rows=self.rows, cols=self.cols)
        illustration = ILLUSTRATIONS.get(self.current)
        if illustration:
            # Center the 3x15 illustration on the board
            row_offset = (self.rows - 3) // 2
            col_offset = (self.cols - 15) // 2
            for row_idx, row_codes in enumerate(illustration.grid):
                target_row = row_idx + row_offset
                if target_row < self.rows:
                    # Pad row_codes to center horizontally
                    padded = [0] * col_offset + row_codes + [0] * (self.cols - col_offset - 15)
                    board.set_row(target_row, padded[:self.cols])
        return board

    def set_illustration(self, slug: str) -> None:
        """Change the current illustration."""
        if slug in ILLUSTRATIONS:
            self.current = slug

    def get_illustrations(self) -> list[tuple[str, str]]:
        """Return list of (slug, name) for UI dropdowns."""
        return [(slug, ill.name) for slug, ill in ILLUSTRATIONS.items()]
