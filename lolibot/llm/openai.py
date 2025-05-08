"""OpenAI provider implementation."""

import json
import logging
import requests

from lolibot.config import BotConfig
from .base import LLMProvider
from .prompts import common_prompt

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def name(self) -> str:
        return "OpenAI"

    def __init__(self, config: BotConfig):
        self.__api_key = config.openai_api_key

    def process_text(self, text) -> dict:
        """Process text with OpenAI API."""
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.__api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": common_prompt(),
                    },
                    {"role": "user", "content": text},
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
        )
        result = response.json()
        logger.debug(f"OpenAI response: {result}")
        if "error" in result:
            raise Exception(result["error"]["message"])
        return json.loads(result["choices"][0]["message"]["content"])

    def check_connection(self) -> bool:
        """Ping OpenAI API to check if it's reachable."""
        try:
            response = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {self.__api_key}"})
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error pinging OpenAI: {e}")
            return False
