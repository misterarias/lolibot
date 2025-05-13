"""Task management module for handling tasks, events, and reminders."""

import logging
from lolibot import UnknownTaskException
from lolibot.config import BotConfig
from lolibot.google_api import create_task, create_calendar_event, create_reminder
from lolibot.db import save_task_to_db
from lolibot.services import TaskData

logger = logging.getLogger(__name__)


class TaskManager:
    """Manage tasks, events, and reminders."""

    def __init__(self, config: BotConfig):
        self.config = config

    def process_task(self, user_id, message, task_data: TaskData):
        """Process a task and create it in the appropriate service."""
        google_id = None
        confirmation = None
        if task_data.task_type == "task":
            google_id = create_task(self.config, task_data)
            confirmation = "Task created"
        elif task_data.task_type == "event":
            google_id = create_calendar_event(self.config, task_data)
            confirmation = "Calendar event created"
        elif task_data.task_type == "reminder":
            google_id = create_reminder(self.config, task_data)
            confirmation = "Reminder set"
        else:
            raise UnknownTaskException(f"Unknown task type: {task_data.task_type}")
        save_task_to_db(user_id, message, task_data, google_id)

        time_str = f" at {task_data.time}" if task_data.time else ""
        if google_id:
            response = (
                f"{confirmation}! 👍\n\n"
                f"Title: {task_data.title}\n"
                f"When: {task_data.date}{time_str}\n"
                f"Type: {task_data.task_type.capitalize()}"
            )
            if task_data.invitees:
                response += f"\nInvitees: {', '.join(task_data.invitees)}"
        else:
            response = (
                f"I understood your request, but couldn't create the {task_data.task_type} "
                f"in Google. I've saved it locally and will retry later."
            )
        return response
