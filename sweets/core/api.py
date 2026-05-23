"""Vestaboard API client implementations."""

import time
from abc import ABC, abstractmethod

import requests

from sweets.core.board import Board, DEFAULT_ROWS, DEFAULT_COLS


class RateLimitError(Exception):
    """Raised when Vestaboard API rate limit is hit."""
    pass


class VestaboardClient(ABC):
    """Abstract base class for Vestaboard API clients."""

    @abstractmethod
    def read(self) -> Board:
        """Get current board state."""
        pass

    @abstractmethod
    def write(self, board: Board) -> bool:
        """Send board state, return success."""
        pass


class CloudClient(VestaboardClient):
    """Vestaboard Cloud API client at https://cloud.vestaboard.com."""

    def __init__(self, api_token: str) -> None:
        self.api_token = api_token
        self.base_url = "https://cloud.vestaboard.com"

    def _headers(self) -> dict[str, str]:
        return {
            "X-Vestaboard-Token": self.api_token,
            "Content-Type": "application/json",
        }

    def read(self, rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS) -> Board:
        """Get current board state from API."""
        response = requests.get(f"{self.base_url}/", headers=self._headers())
        response.raise_for_status()

        data = response.json()
        layout = data.get("currentMessage", {}).get("layout", [])

        board = Board(rows=rows, cols=cols)
        for i, row in enumerate(layout[:rows]):
            board.set_row(i, row[:cols])

        return board

    def write(self, board: Board, retry: bool = True) -> bool:
        """Send board state to API.

        Args:
            board: Board to send
            retry: If True, wait and retry on rate limit (409)

        Raises:
            RateLimitError: If rate limited and retry=False
        """
        payload = {"characters": board.to_array()}
        response = requests.post(
            f"{self.base_url}/",
            headers=self._headers(),
            json=payload,
        )

        if response.status_code == 409:
            if retry:
                # Rate limited - wait and retry once
                time.sleep(15)
                response = requests.post(
                    f"{self.base_url}/",
                    headers=self._headers(),
                    json=payload,
                )
                if response.status_code == 409:
                    raise RateLimitError("Rate limited by Vestaboard API. Please wait ~15 seconds between writes.")
            else:
                raise RateLimitError("Rate limited by Vestaboard API. Please wait ~15 seconds between writes.")

        response.raise_for_status()
        return True


class LocalClient(VestaboardClient):
    """Vestaboard Local API client (stubbed for future implementation)."""

    def __init__(self, api_key: str, host: str = "vestaboard.local") -> None:
        self.api_key = api_key
        self.base_url = f"http://{host}:7000"

    def read(self) -> Board:
        """Get current board state from local API."""
        raise NotImplementedError("LocalClient not yet implemented")

    def write(self, board: Board) -> bool:
        """Send board state to local API."""
        raise NotImplementedError("LocalClient not yet implemented")
