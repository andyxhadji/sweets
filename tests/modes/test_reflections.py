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
