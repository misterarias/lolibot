"""Configuration module ."""

from dataclasses import dataclass
import logging
from typing import Optional
import tomli
from pathlib import Path

import tomli_w

logger = logging.getLogger(__name__)


@dataclass
class Config:
    # Name of current configuration context
    current_context: str

    # Path to the configuration file used
    config_path: Optional[Path] = None

    # current configuration contexts
    contexts: dict = None

    @property
    def available_contexts(self) -> list:
        return [c for c in self.contexts.keys() if c != "default"]

    def to_file(self):
        """Save the current configuration to the configuration file."""
        if self.config_path is None:
            raise ValueError("Configuration path is not set.")

        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Default context is actually the base configuration
        flat_config = dict(self.contexts["default"])
        flat_config["current_context"] = self.current_context
        contexts = {context_name: context_config for context_name, context_config in self.contexts.items() if context_name != "default"}
        flat_config["context"] = contexts
        with open(self.config_path, "wb") as f:
            tomli_w.dump(flat_config, f)

    @classmethod
    def from_file(cls, config_path: Path = Path("config.toml")) -> "Config":
        """Load configuration from TOML file.
        Args:
            config_path: Path to the TOML configuration file

        Returns:
            Config object with the loaded configuration of the appropriate class type
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
        for context_name, context_config in all_contexts.items():
            contexts[context_name] = context_config

        return cls(contexts=contexts, config_path=config_path, current_context=current_context)

    def change_context(self, new_context: str):
        """Save new context to the configuration file. 'default' is not allowed if other contexts exist."""
        switchable = self.available_contexts
        if new_context not in switchable:
            raise ValueError(f"Context '{new_context}' not found in available contexts.")

        if new_context == "default":
            raise ValueError("Context 'default' is not allowed as a explicit configuration context.")

        self.current_context = new_context
        self.to_file()

    def __getattribute__(self, name):
        try:
            # First try normal attribute lookup
            return super().__getattribute__(name)
        except AttributeError:
            # If that fails, try our dynamic config lookup
            contexts = super().__getattribute__("contexts")
            current_context = super().__getattribute__("current_context")

            # Check if the attribute exists in the current context
            if name in contexts[current_context]:
                return contexts[current_context][name]
            # Check if the attribute exists in the default context
            elif name in contexts["default"]:
                return contexts["default"][name]

        # phew----
        return None


class BotConfig(Config):
    """Bot configuration loaded from TOML file."""

    def get_creds_path(self) -> Path:
        """Get the path to the credentials file based on current context."""
        # Assuming the credentials file is in the same directory as this module
        creds_path = Path(".creds") / self.current_context
        if not creds_path.exists():
            creds_path.mkdir(parents=True, exist_ok=True)
        return creds_path
