"""LLM processing module for natural language understanding."""

import abc
import logging
import random
import re
import json
from datetime import datetime, timedelta
import requests


logger = logging.getLogger(__name__)


def common_prompt(text: str = None) -> str:
    if text is None:
        core_text = "Extract task information from user message."
    else:
        core_text = f"Extract task information from this message: '{text}'"

    return f"""\
{core_text}
Identify if the user wants to create a task, a new calendar event, or to set a reminder.
Dates can never be set to the past, it does not make sense.
Extact the date and time from the 'title' field if possible.

Return ONLY a JSON object with:
{{
    "task_type": "task", "event", or "reminder",
    "title": "brief title",
    "description": "detailed description",
    "date": "YYYY-MM-DD" (extract date or use today if not specified),
    "time": "HH:MM" (extract time or null if not specified)
}}
"""


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


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def name(self) -> str:
        return "OpenAI"

    def __init__(self):
        from lolibot.config import OPENAPI_API_KEY

        self.__api_key = OPENAPI_API_KEY

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


class AnthropicProvider(LLMProvider):
    """Anthropic LLM provider."""

    def name(self):
        return "Anthropic"

    def __init__(self):
        from lolibot.config import CLAUDE_API_KEY

        self.__api_key = CLAUDE_API_KEY

    def check_connection(self):
        try:
            response = requests.get("https://api.anthropic.com/v1/models", headers={
                "x-api-key": self.__api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            })
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

        # Extract the JSON from the text
        content = result["content"][0]["text"]
        match = re.search(r"{.*}", content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise Exception("Failed to extract JSON from response")


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""

    def name(self):
        return "Gemini"

    def __init__(self):
        from lolibot.config import GEMINI_API_KEY

        self.__api_key = GEMINI_API_KEY

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
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": common_prompt(text)
                            }
                        ]
                    }
                ],
                "generationConfig": {"temperature": 0.2},
            },
        )
        result = response.json()
        logger.debug(f"Gemini response: {result}")

        content = result["candidates"][0]["content"]["parts"][0]["text"]
        # Extract the JSON from the text
        match = re.search(r"{.*}", content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise Exception("Failed to extract JSON from response")


class DefaultProvider(LLMProvider):
    """Default LLM provider for regex-based parsing."""

    def name(self) -> str:
        return "RegexBased"

    def check_connection(self):
        return True  # Always reachable

    def process_text(self, text) -> dict:
        """
        Fallback method using regex patterns to extract task info
        when LLM processing fails or is not configured.
        """
        # Default values
        today = datetime.now().strftime("%Y-%m-%d")

        result = {
            "task_type": "task",  # Default to task
            "title": text[:50] + ("..." if len(text) > 50 else ""),
            "description": text,
            "date": today,
            "time": None,
        }

        # Try to extract dates
        date_patterns = [
            r"(today|tomorrow|next\s+monday|next\s+tuesday|next\s+wednesday|next\s+thursday|next\s+friday|next\s+saturday|next\s+sunday)",
            r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?))",
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{1,2}/\d{1,2}/\d{2,4})",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text.lower())
            if match:
                date_str = match.group(1)
                # Convert to YYYY-MM-DD format...
                # This is simplified - a real implementation would handle
                # all date formats properly
                if date_str == "today":
                    result["date"] = today
                elif date_str == "tomorrow":
                    result["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                elif date_str.startswith("next"):
                    # Handle "next Monday", etc.
                    day_name = date_str.split()[1]
                    # Map day names to numbers
                    day_map = {
                        "monday": 0,
                        "tuesday": 1,
                        "wednesday": 2,
                        "thursday": 3,
                        "friday": 4,
                        "saturday": 5,
                        "sunday": 6,
                    }
                    target_day = day_map.get(day_name, 0)
                    current_day = datetime.now().weekday()
                    days_ahead = target_day - current_day
                    if days_ahead <= 0:  # Target day already happened this week
                        days_ahead += 7
                    result["date"] = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
                break

        # Try to extract time
        time_pattern = r"(\d{1,2}):(\d{2})(?:\s*(am|pm))?"
        time_match = re.search(time_pattern, text.lower())
        if time_match:
            hour, minute, ampm = time_match.groups()
            hour = int(hour)
            if ampm == "pm" and hour < 12:
                hour += 12
            elif ampm == "am" and hour == 12:
                hour = 0
            result["time"] = f"{hour:02d}:{minute}"

        # Try to identify task type
        if re.search(r"meet(?:ing)?|call|discuss|talk|conversation", text.lower()):
            result["task_type"] = "event"
        elif re.search(r"remind(?:er)?|alert|notify", text.lower()):
            result["task_type"] = "reminder"

        logger.info(f"Regex processing result: {result}")
        return result


class LLMProcessor:
    """Process natural language using LLM APIs."""

    PROVIDERS = [OpenAIProvider(), AnthropicProvider(), GeminiProvider()]

    def process_text(self, text) -> dict:
        """
        Randomly select first working LLM
        """
        llm_providers = random.sample(self.PROVIDERS, len(self.PROVIDERS))
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
            return DefaultProvider().process_text(text)
        return response
