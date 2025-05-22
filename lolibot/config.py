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

    # Name of current configuration context
    current_context: str

    # Path to the configuration file used
    config_path: Optional[Path] = None

    # current configuration contexts
    contexts: dict = None

    # Name of the bot, will be appended to messages
    @property
    def bot_name(self) -> str:
        return self.contexts[self.current_context].get("bot_name")

    # Default timezone for bot-created events
    @property
    def default_timezone(self) -> str:
        return self.contexts[self.current_context].get("default_timezone")

    # Telegram chat ID for relaying telegram exceptions to.
    @property
    def telegram_feedback_chat_id(self) -> str:
        return self.contexts[self.current_context].get("telegram_feedback_chat_id", None)

    # API key for OpenAI ChatGPT
    @property
    def openai_api_key(self) -> str:
        return self.contexts[self.current_context].get("openai_api_key", None)

    # API key for Gemini Flash
    @property
    def gemini_api_key(self) -> str:
        return self.contexts[self.current_context].get("gemini_api_key", None)

    # API key for Claude
    @property
    def claude_api_key(self) -> str:
        return self.contexts[self.current_context].get("claude_api_key", None)

    # Telegram bot token
    @property
    def telegram_token(self) -> str:
        return self.contexts[self.current_context].get("telegram_bot_token", None)

    # List of default invitees for the bot
    @property
    def default_invitees(self) -> list:
        return self.contexts[self.current_context].get("default_invitees", [])

    def get_creds_path(self) -> Path:
        """Get the path to the credentials file based on current context."""
        # Assuming the credentials file is in the same directory as this module
        creds_path = Path(".creds") / self.current_context
        if not creds_path.exists():
            creds_path.mkdir(parents=True, exist_ok=True)
        return creds_path

    @property
    def available_contexts(self) -> list:
        return [c for c in self.contexts.keys() if c != "default"]


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
        lolibot_config = tomli.load(f)

    current_context = lolibot_config.get("current_context", "default")
    all_contexts = lolibot_config.get("context", {})
    if "default" in all_contexts:
        raise ValueError("Context 'default' is not allowed as a explicit configuration context.")

    # default context is the one that is used if no context is specified
    default_context = dict(lolibot_config)
    for key in ["current_context", "context"]:
        if key in default_context:
            del default_context[key]
    contexts = {"default": default_context}

    # merge default context with all contexts
    for _context in all_contexts.keys():
        context_config = {**default_context, **all_contexts[_context]}
        contexts[_context] = context_config

    return BotConfig(contexts=contexts, config_path=config_path, current_context=current_context)


def change_context(new_context: str, config: BotConfig) -> BotConfig:
    """Save new context to the configuration file. 'default' is not allowed if other contexts exist."""
    switchable = config.available_contexts
    if new_context not in switchable:
        raise ValueError(f"Context '{new_context}' not found in available contexts.")

    if new_context == "default":
        raise ValueError("Context 'default' is not allowed as a explicit configuration context.")

    with open(config.config_path, "rb") as f:
        config_data = tomli.load(f)
    config_data["current_context"] = new_context
    with open(config.config_path, "wb") as f:
        tomli_w.dump(config_data, f)
    return load_config(config.config_path)
