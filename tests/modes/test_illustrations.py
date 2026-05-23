"""Tests for illustrations mode."""

import pytest

from sweets.modes.illustrations import IllustrationsMode, ILLUSTRATIONS


def test_render_default_illustration():
    """Mode renders duck by default."""
    mode = IllustrationsMode(rows=3, cols=15)
    board = mode.render()
    assert board.to_array() == ILLUSTRATIONS["duck"].grid


def test_set_illustration():
    """Can switch between illustrations."""
    mode = IllustrationsMode(rows=3, cols=15)
    mode.set_illustration("duck")  # Only duck exists for now
    assert mode.current == "duck"


def test_set_invalid_illustration():
    """Invalid slug is ignored."""
    mode = IllustrationsMode(rows=3, cols=15)
    mode.set_illustration("nonexistent")
    assert mode.current == "duck"


def test_get_illustrations():
    """Returns all available illustrations."""
    mode = IllustrationsMode(rows=3, cols=15)
    options = mode.get_illustrations()
    assert ("duck", "Duck") in options


def test_configure_default():
    """Config can set default illustration."""
    mode = IllustrationsMode(rows=3, cols=15)
    mode.configure({"default": "duck"})
    assert mode.current == "duck"


def test_configure_empty():
    """Empty config keeps default."""
    mode = IllustrationsMode(rows=3, cols=15)
    mode.configure({})
    assert mode.current == "duck"
