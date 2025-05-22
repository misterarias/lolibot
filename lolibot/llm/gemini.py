"""Google Gemini provider implementation."""

from datetime import datetime
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

    def enabled(self) -> bool:
        """Check if the Gemini provider is enabled."""
        return self.__api_key is not None

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
        today = datetime.now().date()
        prompt = f"""\
You are a helpful assistant.
Please provide a JSON response to the following request: '{text}'

Text represents something i need to do. Default 'task_type' to 'task'.

DO NOT CREATE ANY EVENT OR TASK. Just return the JSON object.
For date, extract date from event or use {today} if not specified.
Time can be AM/PM or 24-hour format.
Time can end on "h", such as 12:00h, that is 24-hour format. No ending suffix for time is 24-hour format.
If a time and date is set, task_type should be 'event'.

task_type can only be 'task' or 'event'.

Never ever return a date before {today}, use null instead.
Return ONLY a JSON object with:
{{
    "task_type": "'task' or 'event' as especified",
    "title": "brief title, max 6 words",
    "description": "detailed description",
    "date": "YYYY-MM-DD or null",
    "time": "HH:MM or null"
}}"""
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.__api_key}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        result = response.json()
        logger.debug(f"Gemini response: {result}")

        content = result["candidates"][0]["content"]["parts"][0]["text"]
        # Extract the JSON from the text
        match = re.search(r"{.*}", content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise Exception("Failed to extract JSON from response")
