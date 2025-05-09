"""Configuration module ."""

from dataclasses import dataclass
import logging
from typing import Optional
import tomli
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BotConfig:
    """Bot configuration loaded from TOML file."""

    bot_name: str
    default_timezone: str
    context_name: str
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None

    def get_creds_path(self) -> Path:
        """Get the path to the credentials file based on current context."""
        # Assuming the credentials file is in the same directory as this module
        creds_path = Path(".creds") / self.context_name
        if not creds_path.exists():
            creds_path.mkdir(parents=True, exist_ok=True)
        return creds_path


def load_config(config_path: Path = Path("config.toml")) -> BotConfig:
    """Load configuration from TOML file.
    Args:
        config_path: Path to the TOML configuration file

    Returns:
        BotConfig object with the loaded configuration
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "rb") as f:
        config_data = tomli.load(f)

    # Get the current context
    lolibot_config = config_data.get("lolibot", {})
    context_name = lolibot_config.get("current_context", "default")

    # Get base configuration
    base_config = {
        "bot_name": lolibot_config.get("bot_name"),
        "default_timezone": lolibot_config.get("default_timezone"),
        "context_name": context_name,
    }

    # merge base with default context configuration
    default_context = config_data.get("context", {}).get("default", {})
    base_config = {**base_config, **default_context}

    # Get context-specific configuration
    context_config = config_data.get("context", {}).get(context_name, {})

    # Merge configurations
    final_config = {**base_config, **context_config}

    return BotConfig(**final_config)
