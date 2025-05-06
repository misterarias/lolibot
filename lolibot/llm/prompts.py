"""Common prompt utilities for LLM providers."""


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
