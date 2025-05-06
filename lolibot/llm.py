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
        from lolibot.config import OPENAI_API_KEY

        self.__api_key = OPENAI_API_KEY

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
                "contents": [{"parts": [{"text": common_prompt(text)}]}],
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

    # Day name mappings for both English and Spanish
    DAY_MAP = {
        # English
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6,
        # Spanish
        "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
        "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5,
        "domingo": 6,
    }

    MONTH_MAP = {
        # English
        "jan": 1, "january": 1,
        "feb": 2, "february": 2,
        "mar": 3, "march": 3,
        "apr": 4, "april": 4,
        "may": 5,
        "jun": 6, "june": 6,
        "jul": 7, "july": 7,
        "aug": 8, "august": 8,
        "sep": 9, "september": 9,
        "oct": 10, "october": 10,
        "nov": 11, "november": 11,
        "dec": 12, "december": 12,
        # Spanish
        "ene": 1, "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abr": 4, "abril": 4,
        "mayo": 5,
        "jun": 6, "junio": 6,
        "jul": 7, "julio": 7,
        "ago": 8, "agosto": 8,
        "sep": 9, "septiembre": 9,
        "oct": 10, "octubre": 10,
        "nov": 11, "noviembre": 11,
        "dic": 12, "diciembre": 12,
    }

    def name(self) -> str:
        return "RegexBased"

    def check_connection(self):
        return True  # Always reachable

    def _extract_task_type(self, text: str) -> str:
        """Extract task type from text. Order matters for pattern matching."""
        text = text.lower()
        if re.search(r"remind(?:er)?|alert|notify|recordar|alertar|avisar|recordatorio", text):
            return "reminder"
        elif re.search(r"meet(?:ing)?|call|discuss|talk|conversation|reuni[óo]n|llamada|charla|hablar|discutir", text):
            return "event"
        return "task"

    def _is_valid_time(self, hour: int, minute: int) -> bool:
        """Validate hour and minute values."""
        return 0 <= hour <= 23 and 0 <= minute <= 59

    def _parse_time(self, text: str) -> str | None:
        """Extract and validate time from text."""
        # Support both 12h and 24h formats, including Spanish variations
        time_patterns = [
            r"(\d{1,2}):(\d{2})(?:\s*(am|pm))?",  # English 12h/24h
            r"(\d{1,2}):(\d{2})(?:\s*(a\.?m\.?|p\.?m\.?))?",  # Spanish 12h with dots
            r"(\d{1,2}):(\d{2})(?:\s*(?:de la\s+)?(?:mañana|tarde|noche))?",  # Spanish time of day
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                hour, minute = map(int, match.group(1, 2))
                meridian = match.group(3) if len(match.groups()) > 2 else None

                # Handle Spanish time of day references
                if meridian:
                    meridian = meridian.lower().replace('.', '')
                    if meridian in ['pm', 'p.m', 'tarde', 'noche'] and hour < 12:
                        hour += 12
                    elif meridian in ['am', 'a.m', 'mañana'] and hour == 12:
                        hour = 0

                if self._is_valid_time(hour, minute):
                    return f"{hour:02d}:{minute:02d}"
        return None

    def _parse_iso_date(self, date_str: str) -> str | None:
        """Parse ISO format date (YYYY-MM-DD)."""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return date.strftime("%Y-%m-%d")
        except ValueError:
            return None

    def _parse_slash_date(self, date_str: str) -> str | None:
        """Parse dates with slashes (MM/DD/YYYY or DD/MM/YYYY)."""
        try:
            # Try both American and European formats
            for fmt in ["%m/%d/%Y", "%d/%m/%Y"]:
                try:
                    date = datetime.strptime(date_str, fmt)
                    return date.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        except Exception:
            return None
        return None

    def _parse_relative_date(self, text: str) -> str | None:
        """Parse relative dates like 'today', 'tomorrow', 'next monday'."""
        text = text.lower()
        today = datetime.now()

        # Handle English and Spanish variations
        if text in ["today", "hoy"]:
            return today.strftime("%Y-%m-%d")
        elif text in ["tomorrow", "mañana"]:
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif text.startswith(("next ", "proximo ", "próximo ")):
            day_name = text.split()[1]
            target_day = self.DAY_MAP.get(day_name)
            if target_day is not None:
                current_day = today.weekday()
                days_ahead = target_day - current_day
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        return None

    def _parse_textual_date(self, text: str) -> str | None:
        """Parse dates with month names (15th January, 15 de enero)."""
        # English pattern: "15th january", "15 jan"
        # Spanish pattern: "15 de enero", "15 ene"
        patterns = [
            r"(\d{1,2})(?:st|nd|rd|th)?\s+(?:de\s+)?([a-zA-Zé]+)",
            r"(\d{1,2})\s+(?:de\s+)?([a-zA-Zé]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                day, month = match.groups()
                month_num = self.MONTH_MAP.get(month)
                if month_num:
                    try:
                        date = datetime(datetime.now().year, month_num, int(day))
                        # If date is in the past, use next year
                        if date < datetime.now():
                            date = date.replace(year=date.year + 1)
                        return date.strftime("%Y-%m-%d")
                    except ValueError:
                        continue
        return None

    def _extract_date(self, text: str) -> str:
        """Extract date from text trying different formats."""
        text = text.lower()
        
        # Try different date formats in order
        date_parsers = [
            (r"\d{4}-\d{2}-\d{2}", self._parse_iso_date),
            (r"\d{1,2}/\d{1,2}/\d{4}", self._parse_slash_date),
            (r"today|tomorrow|next\s+\w+|hoy|mañana|proximo\s+\w+|próximo\s+\w+", self._parse_relative_date),
            (r"\d{1,2}(?:st|nd|rd|th)?\s+(?:de\s+)?[a-zA-Zé]+", self._parse_textual_date),
        ]

        for pattern, parser in date_parsers:
            match = re.search(pattern, text)
            if match:
                result = parser(match.group(0))
                if result:
                    return result

        # Default to today if no valid date found
        return datetime.now().strftime("%Y-%m-%d")

    def process_text(self, text: str) -> dict:
        """
        Process text to extract task information using regex patterns.
        Supports both English and Spanish input.
        """
        result = {
            "task_type": self._extract_task_type(text),
            "title": text[:50] + ("..." if len(text) > 50 else ""),
            "description": text,
            "date": self._extract_date(text),
            "time": self._parse_time(text),
        }

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
