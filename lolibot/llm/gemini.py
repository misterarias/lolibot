"""Google Gemini provider implementation."""

import json
import logging
import re
import requests

from lolibot.config import BotConfig
from .base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""

    def name(self):
        return "Gemini"

    def __init__(self, config: BotConfig):
        self.__api_key = config.gemini_api_key

    def check_connection(self):
        try:
            response = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={self.__api_key}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error pinging Gemini: {e}")
            return False

    def process_text(self, text) -> dict:
        """Process text with Google Gemini API."""
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.__api_key}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": text}]}]},
        )
        result = response.json()
        logger.debug(f"Gemini response: {result}")

        content = result["candidates"][0]["content"]["parts"][0]["text"]
        # Extract the JSON from the text
        match = re.search(r"{.*}", content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise Exception("Failed to extract JSON from response")
