"""Tests for daily reflections mode."""

from datetime import date
from unittest.mock import patch

import pytest


def test_same_date_returns_same_reflection(tmp_path):
    """Same date seed should always select the same reflection."""
    from sweets.modes.reflections import ReflectionsMode

    reflections_file = tmp_path / "reflections.yaml"
    reflections_file.write_text(
        "- Question one\n- Question two\n- Question three\n"
    )

    mode = ReflectionsMode()
    mode.reflections_path = reflections_file

    fixed_date = date(2026, 5, 22)
    with patch("sweets.modes.reflections.date") as mock_date:
        mock_date.today.return_value = fixed_date
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        board1 = mode.render()
        board2 = mode.render()

    assert board1.to_array() == board2.to_array()


def test_different_dates_select_differently(tmp_path):
    """Different dates should (usually) select different reflections."""
    from sweets.modes.reflections import ReflectionsMode

    reflections_file = tmp_path / "reflections.yaml"
    # Many reflections to make collision unlikely
    reflections_file.write_text(
        "\n".join(f"- Reflection {i}" for i in range(100))
    )

    mode = ReflectionsMode()
    mode.reflections_path = reflections_file

    results = []
    for day_offset in range(10):
        test_date = date(2026, 1, 1 + day_offset)
        with patch("sweets.modes.reflections.date") as mock_date:
            mock_date.today.return_value = test_date
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            board = mode.render()
            results.append(board.to_array())

    # At least some should differ (extremely unlikely all 10 match)
    unique_results = [str(r) for r in results]
    assert len(set(unique_results)) > 1
