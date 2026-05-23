"""Tests for illustrations mode."""

import pytest

from sweets.modes.illustrations import IllustrationsMode, ILLUSTRATIONS


def test_render_default_illustration():
    """Mode renders duck by default."""
    mode = IllustrationsMode(rows=3, cols=15)
    board = mode.render()
    assert board.to_array() == ILLUSTRATIONS["duck"].grid
