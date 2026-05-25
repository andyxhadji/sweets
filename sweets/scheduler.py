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

    def __init__(
        self,
        client: VestaboardClient,
        mode_settings: dict[str, dict[str, Any]] | None = None,
        board_rows: int = 6,
        board_cols: int = 22,
    ) -> None:
        self.client = client
        self.mode_settings = mode_settings or {}
        self.board_rows = board_rows
        self.board_cols = board_cols
        self.active_mode: Mode | None = None
        self._running = False
        self._thread: threading.Thread | None = None
        self._last_update: datetime | None = None
        self._last_board: Board | None = None

    def start(self, mode_slug: str) -> None:
        """Activate a mode and begin background update loop."""
        self.stop()  # Stop any existing mode

        mode = get_mode(mode_slug, rows=self.board_rows, cols=self.board_cols)
        settings = self.mode_settings.get(mode_slug, {})
        mode.configure(settings)

        self.active_mode = mode
        self._running = True

        # Render and write immediately
        self._update()

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

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

    def refresh_current_board(self) -> Board | None:
        """Read the board currently displayed by Vestaboard."""
        try:
            board = self.client.read(rows=self.board_rows, cols=self.board_cols)
        except Exception as e:
            print(f"Error reading current board: {e}")
            return self._last_board

        self._last_board = board
        return board

    def send_message(self, text: str) -> bool:
        """Send a one-off message (doesn't affect active mode)."""
        board = Board.from_text(text, rows=self.board_rows, cols=self.board_cols)
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

    def force_update(self) -> None:
        """Force immediate re-render of current mode."""
        if self.active_mode is not None:
            self._update()

    def _run_loop(self) -> None:
        """Background loop that updates at mode's interval."""
        while self._running and self.active_mode is not None:
            interval = self.active_mode.interval
            # Static modes (interval=None) don't need periodic updates
            if interval is None:
                return
            # Sleep in small increments to allow quick shutdown
            for _ in range(interval):
                if not self._running:
                    return
                time.sleep(1)
            if self._running and self.active_mode is not None:
                self._update()
