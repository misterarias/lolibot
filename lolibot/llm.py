"""LLM processing module for natural language understanding."""
import re
import json
from datetime import datetime, timedelta
import requests
from lolibot.config import LLM_API_KEY, LLM_API_URL, LLM_PROVIDER, logger


class LLMProcessor:
    """Process natural language using LLM APIs."""

    @staticmethod
    def process_text(text):
        """
        Process text with the configured LLM to extract task information.
        Returns structured data about the task.
        """
        if LLM_PROVIDER == "openai":
            return _process_with_openai(text)
        elif LLM_PROVIDER == "anthropic":
            return _process_with_anthropic(text)
        elif LLM_PROVIDER == "gemini":
            return _process_with_gemini(text)
        else:
            # Fallback to regex-based parsing if no LLM is configured
            return _process_with_regex(text)


def _process_with_openai(text):
    """Process text with OpenAI API."""
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": """
                    Extract task information from the user message.
                    Identify if it's a task, calendar event, or reminder.
                    Return a JSON object with:
                    {
                        "task_type": "task", "event", or "reminder",
                        "title": "brief title",
                        "description": "detailed description",
                        "date": "YYYY-MM-DD" (extract date or use today if not specified),
                        "time": "HH:MM" (extract time or null if not specified)
                    }
                    """,
                    },
                    {"role": "user", "content": text},
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
        )
        result = response.json()
        return json.loads(result["choices"][0]["message"]["content"])
    except Exception as e:
        logger.error(f"Error processing with OpenAI: {e}")
        return _process_with_regex(text)


def _process_with_anthropic(text):
    """Process text with Anthropic Claude API."""
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": LLM_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": "claude-instant-1.2",
                "max_tokens": 300,
                "system": """
                Extract task information from the user message.
                Identify if it's a task, calendar event, or reminder.
                Return ONLY a JSON object with:
                {
                    "task_type": "task", "event", or "reminder",
                    "title": "brief title",
                    "description": "detailed description",
                    "date": "YYYY-MM-DD" (extract date or use today if not specified),
                    "time": "HH:MM" (extract time or null if not specified)
                }
                """,
                "messages": [{"role": "user", "content": text}],
            },
        )
        result = response.json()
        # Extract the JSON from the text
        content = result["content"][0]["text"]
        match = re.search(r"{.*}", content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return _process_with_regex(text)
    except Exception as e:
        logger.error(f"Error processing with Anthropic: {e}")
        return _process_with_regex(text)


def _process_with_gemini(text):
    """Process text with Google Gemini API."""
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={LLM_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": f"""
                                Extract task information from this message: "{text}"
                                Identify if it's a task, calendar event, or reminder.
                                Return ONLY a JSON object with:
                                {{
                                    "task_type": "task", "event", or "reminder",
                                    "title": "brief title",
                                    "description": "detailed description",
                                    "date": "YYYY-MM-DD" (extract date or use today if not specified),
                                    "time": "HH:MM" (extract time or null if not specified)
                                }}
                                """
                            }
                        ]
                    }
                ],
                "generationConfig": {"temperature": 0.2},
            },
        )
        result = response.json()
        content = result["candidates"][0]["content"]["parts"][0]["text"]
        # Extract the JSON from the text
        match = re.search(r"{.*}", content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return _process_with_regex(text)
    except Exception as e:
        logger.error(f"Error processing with Gemini: {e}")
        return _process_with_regex(text)


def _process_with_regex(text):
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

    return result
