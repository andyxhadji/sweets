"""Tests for scheduler."""

from unittest.mock import MagicMock

from sweets.core.board import Board
from sweets.scheduler import Scheduler


def test_refresh_current_board_reads_displayed_board():
    """refresh_current_board reads and caches the board from the client."""
    current_board = Board(rows=3, cols=15)
    current_board.center_text(1, "HI")
    client = MagicMock()
    client.read.return_value = current_board
    scheduler = Scheduler(client, board_rows=3, board_cols=15)

    board = scheduler.refresh_current_board()

    assert board is current_board
    assert scheduler.get_last_board() is current_board
    client.read.assert_called_once_with(rows=3, cols=15)


def test_refresh_current_board_falls_back_to_last_board():
    """refresh_current_board returns the cached board if reading fails."""
    last_board = Board(rows=3, cols=15)
    client = MagicMock()
    client.read.side_effect = RuntimeError("network unavailable")
    scheduler = Scheduler(client, board_rows=3, board_cols=15)
    scheduler._last_board = last_board

    board = scheduler.refresh_current_board()

    assert board is last_board


def test_force_update_renders_and_sends():
    """force_update re-renders active mode and sends to board."""
    client = MagicMock()
    client.write.return_value = True
    scheduler = Scheduler(client, board_rows=3, board_cols=15)

    scheduler.start("clock")
    initial_board = scheduler.get_last_board()

    scheduler.force_update()

    assert scheduler.get_last_board() is not None
    assert client.write.called


def test_force_update_no_active_mode():
    """force_update does nothing if no active mode."""
    client = MagicMock()
    scheduler = Scheduler(client, board_rows=3, board_cols=15)

    scheduler.force_update()  # Should not raise

    assert not client.write.called
