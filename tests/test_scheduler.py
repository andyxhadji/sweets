"""Tests for scheduler."""

from unittest.mock import MagicMock

from sweets.scheduler import Scheduler


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


def test_start_static_mode_no_interval():
    """Starting a mode with interval=None works without crashing."""
    client = MagicMock()
    client.write.return_value = True
    scheduler = Scheduler(client, board_rows=3, board_cols=15)

    # Drawing mode has interval=None
    grid = [[0] * 15 for _ in range(3)]
    scheduler.mode_settings["drawing"] = {"grid": grid}
    scheduler.start("drawing")

    # Should have rendered and written once
    assert scheduler.get_last_board() is not None
    assert client.write.called
    assert scheduler.active_mode is not None
    assert scheduler.active_mode.slug == "drawing"

    scheduler.stop()
