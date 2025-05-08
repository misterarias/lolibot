"""Common prompt utilities for LLM providers."""


def common_prompt(text: str = None) -> str:
    if text is None:
        core_text = "Extract information from user message."
    else:
        core_text = f"Extract information from this message: '{text}'."

    return f"""\
{core_text}
Identify if the user wants to create a "task", a new calendar "event", or to set a "reminder" to do something.
The user may provide a date or a time, but they are not required.
'date' and 'time' fields, when filled, must always be in the future.
That means that dates before today or times before the current time are not valid.
Extact the date and time from the 'title' field, when informed.
Add emojis that are relevant to the task type.
If the task title is longer than 50 characters, truncate it to 50 characters and add "..." at the end.

Return ONLY a JSON object with:
{{
    "task_type": "task", "event", or "reminder",
    "title": "brief title",
    "description": "detailed description",
    "date": "YYYY-MM-DD" (extract date or use today if not specified, never before today),
    "time": "HH:MM" (extract time or null if not specified)
}}
"""
