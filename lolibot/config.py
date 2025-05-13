"""Configuration module ."""

from dataclasses import dataclass
import logging
from typing import Optional
import tomli
from pathlib import Path

import tomli_w

logger = logging.getLogger(__name__)


@dataclass()
class BotConfig:
    """Bot configuration loaded from TOML file."""

    bot_name: str
    default_timezone: str
    context_name: str
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    available_contexts: list[str] = None
    config_path: Optional[Path] = None
    default_invitees: Optional[list[str]] = None

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
        "available_contexts": list(config_data.get("context", {}).keys()),
        "config_path": config_path,
    }

    # merge base with default context configuration
    default_context = config_data.get("context", {}).get("default", {})
    base_config = {**base_config, **default_context}

    # Get context-specific configuration
    context_config = config_data.get("context", {}).get(context_name, {})

    # Extract invitees and aliases if present
    default_invitees = context_config.get("default_invitees") or base_config.get("default_invitees")
    final_config = {**base_config, **context_config}

    final_config["default_invitees"] = default_invitees
    return BotConfig(**final_config)


def change_context(new_context: str, config: BotConfig) -> BotConfig:
    """Save new context to the configuration file."""
    if new_context not in config.available_contexts:
        raise ValueError(f"Context '{new_context}' not found in available contexts.")

    with open(config.config_path, "rb") as f:
        config_data = tomli.load(f)

    config_data["lolibot"]["current_context"] = new_context
    with open(config.config_path, "wb") as f:
        tomli_w.dump(config_data, f)

    return load_config(config.config_path)
