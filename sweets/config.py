"""Configuration loading and validation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Config:
    """Application configuration."""

    board_rows: int = 6
    board_cols: int = 22
    api_type: str = "cloud"
    api_host: str = "vestaboard.local"
    cloud_api_token: str = ""
    local_api_key: str | None = None
    default_mode: str = "clock"
    modes: dict[str, dict[str, Any]] = field(default_factory=dict)
    web_host: str = "127.0.0.1"
    web_port: int = 5000


def load_config(
    config_path: Path | None = None,
    secrets_path: Path | None = None,
) -> Config:
    """Load configuration from config.yaml and secrets.yaml.

    Args:
        config_path: Path to config.yaml (defaults to ./config.yaml)
        secrets_path: Path to secrets.yaml (defaults to ./secrets.yaml)

    Returns:
        Validated Config object

    Raises:
        FileNotFoundError: If config files don't exist
        ValueError: If required fields are missing
    """
    if config_path is None:
        config_path = Path("config.yaml")
    if secrets_path is None:
        secrets_path = Path("secrets.yaml")
        if not secrets_path.exists():
            secrets_path = Path.home() / ".config" / "sweets" / "secrets.yaml"

    # Load main config
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config_data = yaml.safe_load(f) or {}

    # Load secrets (optional - may not exist yet)
    secrets_data: dict[str, Any] = {}
    if secrets_path.exists():
        with open(secrets_path) as f:
            secrets_data = yaml.safe_load(f) or {}

    # Build config object
    board_config = config_data.get("board", {})
    api_config = config_data.get("api", {})
    web_config = config_data.get("web", {})

    config = Config(
        board_rows=board_config.get("rows", 6),
        board_cols=board_config.get("cols", 22),
        api_type=api_config.get("type", "cloud"),
        api_host=api_config.get("host", "vestaboard.local"),
        cloud_api_token=secrets_data.get("cloud_api_token", ""),
        local_api_key=secrets_data.get("local_api_key"),
        default_mode=config_data.get("default_mode", "clock"),
        modes=config_data.get("modes", {}),
        web_host=web_config.get("host", "127.0.0.1"),
        web_port=web_config.get("port", 5000),
    )

    return config
