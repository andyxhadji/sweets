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


def test_all_illustrations_valid():
    """All illustrations have valid 3x15 grids."""
    for slug, ill in ILLUSTRATIONS.items():
        assert len(ill.grid) == 3, f"{slug} should have 3 rows"
        for row in ill.grid:
            assert len(row) == 15, f"{slug} rows should have 15 cols"
            for code in row:
                assert 0 <= code <= 70, f"{slug} has invalid code {code}"


def test_illustration_count():
    """Should have 15 illustrations."""
    assert len(ILLUSTRATIONS) == 15
