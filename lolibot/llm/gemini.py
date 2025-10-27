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
        return "Gemini Flash 2.5"

    def enabled(self) -> bool:
        """Check if the Gemini provider is enabled."""
        return self.__api_key is not None

    def __init__(self, config: BotConfig):
        self.__api_key = config.gemini_api_key

    def __post_prompt(self, prompt: str) -> str:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.__api_key}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        result = response.json()
        logger.debug(f"Gemini response: {result}")

        content = result["candidates"][0]["content"]["parts"][0]["text"]
        return content

    def check_connection(self):
        try:
            response = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={self.__api_key}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error pinging Gemini: {e}")
            return False

    def split_text(self, text) -> list:
        prompt = f"""\
You are a helpful assistant, your task is to split the following text into smaller tasks that can be processed individually.
A task is something that needs to be done, that will be fed into another LLM for processing.

It is very important that the message is preserved, commas might appear in the text.
Do not blindly split by commas just because they are there.

Examples
- "We must go to the store, buy groceries, and clean the house." is three tasks.
- "make sure that you buy apples, oranges, and bananas" is one task.

If the text contains multiple tasks, split them into individual tasks.
If the text contains only one task, return just one task.
If just one temporal reference is present, add it to all tasks.
If more than one temporal reference is present, split tasks accordingly.

Please provide a JSON response to the following request: '{text}' with a list for each task.

Clean linking terms in the language the text is written in, such as "and", "y", "e", "then", "luego", etc.
Examples:
Input: "Go to the store, buy groceries, and clean the house."
Output: ["Go to the store", "Buy groceries", "Clean the house"]

Input: "crerar una reunión el próximo martes a las 10h y enviar el informe mensual."
Output: ["Crear una reunión el próximo martes a las 10h", "Enviar el informe mensual el próximo martes a las 10h"]

NEVER CREATE ANY EVENT OR TASK, that is not your job.
Always return a JSON array of strings.

"""
        response = self.__post_prompt(prompt)
        logger.debug(f"Split tasks response: {response}")

        # text is in format: ```json [ ... ] ```
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if not match:
            raise Exception("Failed to extract JSON array from response")

        json_data = json.loads(match.group(0))
        logger.info(f"Split tasks JSON: {json_data}")
        return json_data

    def process_text(self, text) -> dict:
        """Process text with Google Gemini API."""
        today = datetime.now().date()
        prompt = f"""\
You are a helpful assistant, your task is to extract a task or event from the text provided.
A task is something that needs to be done, an event is something that happens at a specific date and, optionally, time.

Please provide a JSON response to the following request: '{text}' with only the following keys:

"task_type" can only be 'task' or 'event'.
"title" is a summary you create from the text.
"description" is the full text provided, it can be empty if not specified, and can be enhanced with expanded dates or locations.
"date" is either "YYYY-MM-DD" or null if no date is specified.
"time" is either "HH:MM" or null if no time is specified.
"duration" is the duration in minutes of the event, if any. Default to 30 minutes


NEVER CREATE ANY EVENT OR TASK.
Always return a JSON object.
For date, extract date from event. Date can come in many formats, such as: 17/07/2024, 7 de Julio, el próximo martes....
If text contains "tomorrow", "next week", "next month", "next year", or similar, use {today} + 1 day, 7 days, 30 days, 365 days...

Use {today} if no date specified.
Time can be AM/PM or 24-hour format.
Time can end on "h", such as 12:00h, that is 24-hour format. No ending suffix for time is 24-hour format.
It is illegal to return an empty or invalid date for events.
"""
        content = self.__post_prompt(prompt)

        # Extract the JSON from the text
        match = re.search(r"{.*}", content, re.DOTALL)
        if not match:
            raise Exception("Failed to extract JSON from response")

        response = match.group(0)
        json_date = json.loads(response)
        logger.info(f"Extracted JSON: {json_date}")
        return json_date
