"""Shared test fixtures."""

from pathlib import Path

import pytest
import responses

from sweets.core.board import Board
from sweets.config import Config


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


@pytest.fixture
def test_config() -> Config:
    """Config object with test values."""
    return Config(
        api_type="cloud",
        api_host="vestaboard.local",
        cloud_api_token="test-token",
        local_api_key=None,
        default_mode="clock",
        modes={"clock": {"format": "12h", "show_seconds": False}},
        web_host="127.0.0.1",
        web_port=5000,
    )


@pytest.fixture
def temp_config_files(tmp_path: Path) -> tuple[Path, Path]:
    """Create temporary config files for testing."""
    config_path = tmp_path / "config.yaml"
    secrets_path = tmp_path / "secrets.yaml"

    config_path.write_text("""
api:
  type: cloud
default_mode: clock
modes:
  clock:
    format: 12h
""")

    secrets_path.write_text("""
cloud_api_token: test-token-123
""")

    return config_path, secrets_path
