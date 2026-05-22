"""Mode scheduler for running active mode in background."""

import threading
import time
from datetime import datetime
from typing import Any

from sweets.core.api import VestaboardClient
from sweets.core.board import Board
from sweets.modes import get_mode, get_all_modes
from sweets.modes.base import Mode


class Scheduler:
    """Manages the single active mode and its update loop."""

    def __init__(self, client: VestaboardClient, mode_settings: dict[str, dict[str, Any]] | None = None) -> None:
        self.client = client
        self.mode_settings = mode_settings or {}
        self.active_mode: Mode | None = None
        self._running = False
        self._thread: threading.Thread | None = None
        self._last_update: datetime | None = None
        self._last_board: Board | None = None

    def start(self, mode_slug: str) -> None:
        """Activate a mode and begin background update loop."""
        self.stop()  # Stop any existing mode

        mode = get_mode(mode_slug)
        settings = self.mode_settings.get(mode_slug, {})
        mode.configure(settings)

        self.active_mode = mode
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        # Immediate first update
        self._update()

    def stop(self) -> None:
        """Stop the current mode."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
        self.active_mode = None

    def get_status(self) -> dict[str, Any]:
        """Return current mode status."""
        return {
            "active_mode": self.active_mode.slug if self.active_mode else None,
            "mode_name": self.active_mode.name if self.active_mode else None,
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "running": self._running,
            "available_modes": list(get_all_modes().keys()),
        }

    def get_last_board(self) -> Board | None:
        """Return the last rendered board."""
        return self._last_board

    def send_message(self, text: str) -> bool:
        """Send a one-off message (doesn't affect active mode)."""
        board = Board.from_text(text)
        self._last_board = board
        self._last_update = datetime.now()
        return self.client.write(board)

    def _update(self) -> None:
        """Render and send current mode's board."""
        if self.active_mode is None:
            return

        board = self.active_mode.render()
        self._last_board = board
        self._last_update = datetime.now()

        try:
            self.client.write(board)
        except Exception as e:
            # Log but don't crash the loop
            print(f"Error writing to board: {e}")

    def _run_loop(self) -> None:
        """Background loop that updates at mode's interval."""
        while self._running and self.active_mode is not None:
            time.sleep(self.active_mode.interval)
            if self._running and self.active_mode is not None:
                self._update()
