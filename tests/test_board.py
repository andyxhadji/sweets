"""Tests for Board abstraction."""

from sweets.core.board import Board


def test_board_dimensions():
    """Board should always be 6 rows x 22 columns."""
    board = Board()
    assert len(board.rows) == 6
    for row in board.rows:
        assert len(row) == 22


def test_to_array_format():
    """to_array should return a copy of the grid."""
    board = Board()
    board.rows[0][0] = 1  # Set 'A'

    array = board.to_array()
    assert array[0][0] == 1

    # Modifying returned array shouldn't affect board
    array[0][0] = 99
    assert board.rows[0][0] == 1


def test_set_row():
    """set_row should replace a row, padding or truncating as needed."""
    board = Board()

    # Set row with exact length
    codes = [1, 2, 3] + [0] * 19  # 22 chars
    board.set_row(0, codes)
    assert board.rows[0] == codes

    # Set row with shorter list (should pad with 0s)
    board.set_row(1, [1, 2, 3])
    assert board.rows[1] == [1, 2, 3] + [0] * 19


def test_center_text():
    """center_text should center text on a row."""
    board = Board()

    # "HI" is 2 chars, should have 10 blanks on each side
    board.center_text(0, "HI")
    expected = [0] * 10 + [8, 9] + [0] * 10
    assert board.rows[0] == expected


def test_from_text_simple():
    """from_text should center short messages."""
    board = Board.from_text("HI")

    # "HI" should be centered on middle row (row 2 or 3)
    # Check that HI appears somewhere centered
    found = False
    for row in board.rows:
        text = "".join(chr(64 + c) if 1 <= c <= 26 else " " for c in row).strip()
        if text == "HI":
            found = True
            break
    assert found, "HI should appear centered on the board"


def test_from_text_wrapping():
    """from_text should wrap long text to multiple lines."""
    # 30 chars won't fit on one line (max 22)
    board = Board.from_text("THE QUICK BROWN FOX JUMPS")

    # Should have content on multiple rows
    non_empty_rows = sum(1 for row in board.rows if any(c != 0 for c in row))
    assert non_empty_rows >= 2, "Long text should wrap to multiple rows"
