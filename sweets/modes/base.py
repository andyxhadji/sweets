"""Abstract base class for display modes."""

from abc import ABC, abstractmethod
from typing import Any

from sweets.core.board import Board


class Mode(ABC):
    """Base class for all display modes."""

    name: str = "Unknown"
    slug: str = "unknown"
    interval: int = 60  # seconds between updates

    def configure(self, settings: dict[str, Any]) -> None:
        """Apply mode-specific settings from config.

        Override in subclasses to handle settings.
        """
        pass

    @abstractmethod
    def render(self) -> Board:
        """Generate current board state.

        Returns:
            Board with the current display content
        """
        pass
