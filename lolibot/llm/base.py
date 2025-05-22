"""Base module for LLM providers."""

import abc

from lolibot.config import BotConfig


class LLMProvider(abc.ABC):
    """Abstract base class for LLM providers."""

    @abc.abstractmethod
    def __init__(self, config: BotConfig):
        """Initialize the LLM provider."""
        pass

    @abc.abstractmethod
    def name(self) -> str:
        """Return the name of the LLM provider."""
        pass

    @abc.abstractmethod
    def process_text(self, text) -> dict:
        """Process text using the LLM provider."""
        pass

    @abc.abstractmethod
    def check_connection(self) -> bool:
        pass

    @abc.abstractmethod
    def enabled(self) -> bool:
        """Check if the LLM provider is enabled."""
        pass
