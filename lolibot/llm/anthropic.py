"""Anthropic provider implementation."""

import json
import logging
import re
import requests

from lolibot.config import BotConfig
from .base import LLMProvider
from .prompts import common_prompt

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Anthropic LLM provider."""

    def name(self):
        return "Anthropic"

    def enabled(self) -> bool:
        """Check if the provider is enabled."""
        return self.__api_key is not None

    def __init__(self, config: BotConfig):
        self.__api_key = config.claude_api_key

    def check_connection(self):
        try:
            response = requests.get(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": self.__api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
            )
            logger.debug(f"Anthropic response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error pinging Claude: {e}")
            return False

    def process_text(self, text) -> dict:
        """Process text with Anthropic API."""
        response = requests.post(
            "https://api.anthropic.com/v1/complete",
            headers={
                "x-api-key": self.__api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": "claude-instant-1.2",
                "max_tokens": 300,
                "system": common_prompt(),
                "messages": [{"role": "user", "content": text}],
            },
        )
        result = response.json()
        logger.debug(f"Anthropic response: {result}")
        if result.get("type") == "error":
            raise Exception(f"Error processing text with Claude: {result['error']['message']}")

        # Extract the JSON from the text
        content = result["content"][0]["text"]
        match = re.search(r"{.*}", content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise Exception("Failed to extract JSON from response")
