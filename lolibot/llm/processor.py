"""LLM processor module."""

from typing import List
import random
import logging

from lolibot.config import BotConfig
from lolibot.llm.base import LLMProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .gemini import GeminiProvider
from .default import DefaultProvider

logger = logging.getLogger(__name__)


class LLMProcessor:
    """Process natural language using LLM APIs."""

    def __init__(self, config: BotConfig):
        self.providers = [
            OpenAIProvider(config),
            AnthropicProvider(config),
            GeminiProvider(config),
        ]
        self.default_provider = DefaultProvider(config)

    def __shuffle_providers(self) -> List[LLMProvider]:
        """Randomly select first working LLM."""
        llm_providers = random.sample(self.providers, len(self.providers))
        llm_providers = [p for p in llm_providers if p.enabled()]
        if not llm_providers:
            logger.error("No LLM providers are enabled. Falling back to regex-based parsing.")
            return [self.default_provider]
        return llm_providers

    def split_text(self, text) -> list:
        """
        Split text into smaller chunks if needed.
        Currently, this is a placeholder that returns the text as a single chunk.
        """
        providers = self.__shuffle_providers()
        response = None

        for provider in providers:
            try:
                response = provider.split_text(text)
                break
            except Exception as e:
                logger.warning(f"Error splitting text with {provider.name()}: {e}")

        if not response:
            logger.error("All LLM providers failed. Falling back to regex-based parsing.")
            return self.default_provider.split_text(text)
        return response

    def process_text(self, text) -> dict:
        """
        Randomly select first working LLM
        """
        provider = self.__shuffle_providers()
        response = None

        for provider in provider:
            try:
                response = provider.process_text(text)
                break
            except Exception as e:
                logger.warning(f"Error processing text with {provider.name()}: {e}")

        if not response:
            logger.error("All LLM providers failed. Falling back to regex-based parsing.")
            return self.default_provider.process_text(text)
        return response
