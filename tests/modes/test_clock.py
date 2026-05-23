"""Tests for clock mode."""

from unittest.mock import patch
from datetime import datetime

from sweets.core.board import Board
from sweets.modes.clock import ClockMode


def test_clock_render_returns_board():
    """ClockMode.render() should return a valid Board."""
    mode = ClockMode()
    board = mode.render()

    assert isinstance(board, Board)
    assert len(board.rows) == 6
    assert len(board.rows[0]) == 22


def test_clock_12h_format():
    """ClockMode should show AM/PM in 12h format."""
    mode = ClockMode()
    mode.configure({"format": "12h"})

    # Mock datetime to return a known time
    mock_time = datetime(2026, 5, 22, 14, 30, 0)  # 2:30 PM

    with patch("sweets.modes.clock.datetime") as mock_dt:
        mock_dt.now.return_value = mock_time
        board = mode.render()

    # Find the row with content
    from sweets.core.characters import codes_to_text

    for row in board.rows:
        text = codes_to_text(row).strip()
        if text:
            assert "PM" in text or "AM" in text, f"Expected AM/PM, got: {text}"
            break


def test_clock_24h_format():
    """ClockMode should show 24h time without AM/PM."""
    mode = ClockMode()
    mode.configure({"format": "24h"})

    mock_time = datetime(2026, 5, 22, 14, 30, 0)  # 14:30

    with patch("sweets.modes.clock.datetime") as mock_dt:
        mock_dt.now.return_value = mock_time
        board = mode.render()

    from sweets.core.characters import codes_to_text

    for row in board.rows:
        text = codes_to_text(row).strip()
        if text:
            assert "PM" not in text and "AM" not in text
            assert "14" in text or "4" in text, f"Expected 24h time, got: {text}"
            break
