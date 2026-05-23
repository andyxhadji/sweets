"""Tests for Vestaboard API client."""

import pytest
import responses
import requests

from sweets.core.api import CloudClient
from sweets.core.board import Board


def test_cloud_client_read(mock_cloud_api, sample_board_array):
    """CloudClient.read() should return a Board from API response."""
    mock_cloud_api.add(
        responses.GET,
        "https://cloud.vestaboard.com/",
        json={"currentMessage": {"layout": sample_board_array}},
        status=200,
    )

    client = CloudClient(api_token="test-token")
    board = client.read()

    assert isinstance(board, Board)
    assert board.rows[2][10] == 8  # 'H'
    assert board.rows[2][11] == 9  # 'I'


def test_cloud_client_write(mock_cloud_api, sample_board):
    """CloudClient.write() should POST board as characters array."""
    mock_cloud_api.add(
        responses.POST,
        "https://cloud.vestaboard.com/",
        json={"status": "ok"},
        status=200,
    )

    client = CloudClient(api_token="test-token")
    result = client.write(sample_board)

    assert result is True

    # Verify the request body
    request_body = mock_cloud_api.calls[0].request.body
    assert b'"characters"' in request_body


def test_cloud_client_auth_header(mock_cloud_api, sample_board_array):
    """CloudClient should include X-Vestaboard-Token header."""
    mock_cloud_api.add(
        responses.GET,
        "https://cloud.vestaboard.com/",
        json={"currentMessage": {"layout": sample_board_array}},
        status=200,
    )

    client = CloudClient(api_token="my-secret-token")
    client.read()

    request_headers = mock_cloud_api.calls[0].request.headers
    assert request_headers["X-Vestaboard-Token"] == "my-secret-token"
    assert request_headers["Content-Type"] == "application/json"


def test_cloud_client_error_handling(mock_cloud_api):
    """CloudClient should raise on API errors."""
    mock_cloud_api.add(
        responses.GET,
        "https://cloud.vestaboard.com/",
        json={"error": "Unauthorized"},
        status=401,
    )

    client = CloudClient(api_token="bad-token")

    with pytest.raises(requests.HTTPError):
        client.read()
