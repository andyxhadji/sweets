"""Clock display mode."""

from datetime import datetime
from typing import Any

from sweets.core.board import Board
from sweets.modes.base import Mode


class ClockMode(Mode):
    """Display current time on the board."""

    name = "Clock"
    slug = "clock"
    interval = 60

    def __init__(self) -> None:
        self.format_12h = True
        self.show_seconds = False

    def configure(self, settings: dict[str, Any]) -> None:
        """Apply clock settings."""
        fmt = settings.get("format", "12h")
        self.format_12h = fmt == "12h"
        self.show_seconds = settings.get("show_seconds", False)

    def render(self) -> Board:
        """Generate board with current time."""
        now = datetime.now()

        if self.format_12h:
            if self.show_seconds:
                time_str = now.strftime("%I:%M:%S %p")
            else:
                time_str = now.strftime("%I:%M %p")
        else:
            if self.show_seconds:
                time_str = now.strftime("%H:%M:%S")
            else:
                time_str = now.strftime("%H:%M")

        # Remove leading zero from hour
        time_str = time_str.lstrip("0")

        board = Board()
        board.center_text(2, time_str)

        return board
