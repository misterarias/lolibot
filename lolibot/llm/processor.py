"""LLM processor module."""

import random
import logging

from lolibot.config import BotConfig
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .gemini import GeminiProvider
from .default import DefaultProvider

logger = logging.getLogger(__name__)


class LLMProcessor:
    """Process natural language using LLM APIs."""
    def __init__(self, config: BotConfig):
        self.providers = [OpenAIProvider(config), AnthropicProvider(config), GeminiProvider(config)]
        self.default_provider = DefaultProvider(config)

    def process_text(self, text) -> dict:
        """
        Randomly select first working LLM
        """
        llm_providers = random.sample(self.providers, len(self.providers))
        response = None
        for provider in llm_providers:
            logger.info(f"Using LLM provider: {provider.name()}")
            try:
                response = provider.process_text(text)
                break
            except Exception as e:
                logger.warning(f"Error processing text with {provider.name()}: {e}")
                continue

        if not response:
            logger.error("All LLM providers failed. Falling back to regex-based parsing.")
            return self.default_provider.process_text(text)
        return response
