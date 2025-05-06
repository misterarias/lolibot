"""Base module for LLM providers."""
import abc


class LLMProvider(abc.ABC):
    """Abstract base class for LLM providers."""

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
