"""Tests for drawing mode."""

import pytest

from sweets.modes.drawing import DrawingMode


def test_render_empty_grid():
    """Empty grid config renders blank board."""
    mode = DrawingMode(rows=3, cols=15)
    mode.configure({"grid": []})
    board = mode.render()
    assert board.to_array() == [[0] * 15 for _ in range(3)]


def test_render_with_grid():
    """Grid from config is rendered to board."""
    grid = [
        [63, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 63],
        [0, 63, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 63, 0],
        [0, 0, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 0, 0],
    ]
    mode = DrawingMode(rows=3, cols=15)
    mode.configure({"grid": grid})
    board = mode.render()
    assert board.to_array() == grid


def test_render_truncates_oversized_grid():
    """Grid larger than board is truncated."""
    grid = [[1] * 20 for _ in range(10)]  # 10x20, larger than 3x15
    mode = DrawingMode(rows=3, cols=15)
    mode.configure({"grid": grid})
    board = mode.render()
    arr = board.to_array()
    assert len(arr) == 3
    assert all(len(row) == 15 for row in arr)
    assert all(row == [1] * 15 for row in arr)


def test_render_pads_undersized_grid():
    """Grid smaller than board is padded with zeros."""
    grid = [[63, 64], [65, 66]]  # 2x2, smaller than 3x15
    mode = DrawingMode(rows=3, cols=15)
    mode.configure({"grid": grid})
    board = mode.render()
    arr = board.to_array()
    assert arr[0] == [63, 64] + [0] * 13
    assert arr[1] == [65, 66] + [0] * 13
    assert arr[2] == [0] * 15


def test_mode_attributes():
    """Mode has correct name, slug, and interval."""
    mode = DrawingMode()
    assert mode.name == "Drawing"
    assert mode.slug == "drawing"
    assert mode.interval is None
