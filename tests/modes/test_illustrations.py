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


def test_configure_illustration():
    """Config 'illustration' key sets current illustration."""
    mode = IllustrationsMode(rows=3, cols=15)
    mode.configure({"illustration": "cat"})
    assert mode.current == "cat"


def test_configure_illustration_overrides_default():
    """'illustration' key takes precedence over 'default'."""
    mode = IllustrationsMode(rows=3, cols=15)
    mode.configure({"default": "duck", "illustration": "cat"})
    assert mode.current == "cat"


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


def test_render_on_standard_board():
    """Illustration is centered on 6x22 board."""
    mode = IllustrationsMode(rows=6, cols=22)
    mode.set_illustration("duck")
    board = mode.render()
    arr = board.to_array()

    # Should have 6 rows, 22 cols
    assert len(arr) == 6
    assert all(len(row) == 22 for row in arr)

    # Duck grid is centered: row_offset=1 (6-3)//2, col_offset=3 (22-15)//2
    duck_grid = ILLUSTRATIONS["duck"].grid

    # Rows 0 and 4-5 should be empty
    assert arr[0] == [0] * 22
    assert arr[4] == [0] * 22
    assert arr[5] == [0] * 22

    # Rows 1-3 should have duck content centered (cols 3-17)
    for i, duck_row in enumerate(duck_grid):
        board_row = arr[i + 1]
        # First 3 cols should be 0
        assert board_row[:3] == [0, 0, 0]
        # Middle 15 cols should match duck
        assert board_row[3:18] == duck_row
        # Last 4 cols should be 0
        assert board_row[18:] == [0, 0, 0, 0]


def test_render_on_note_board():
    """Illustration fills Note-sized board exactly."""
    mode = IllustrationsMode(rows=3, cols=15)
    mode.set_illustration("duck")
    board = mode.render()
    arr = board.to_array()

    # Should match duck grid exactly (no offset needed)
    assert arr == ILLUSTRATIONS["duck"].grid


def test_illustration_count():
    """Should have 15 illustrations."""
    assert len(ILLUSTRATIONS) == 15
