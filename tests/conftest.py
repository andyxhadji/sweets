"""Shared test fixtures."""

import pytest
import responses

from sweets.core.board import Board


@pytest.fixture
def sample_board() -> Board:
    """A board with 'HI' centered."""
    board = Board()
    board.center_text(2, "HI")
    return board


@pytest.fixture
def sample_board_array() -> list[list[int]]:
    """API response format for a board with 'HI'."""
    rows = [[0] * 22 for _ in range(6)]
    rows[2] = [0] * 10 + [8, 9] + [0] * 10
    return rows


@pytest.fixture
def mock_cloud_api():
    """Activate responses mock for Vestaboard Cloud API."""
    with responses.RequestsMock() as rsps:
        yield rsps
