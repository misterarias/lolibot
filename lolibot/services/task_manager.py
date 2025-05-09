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
        """Initialize the TaskManager with the bot configuration."""
        self.config = config

    def process_task(self, user_id, message, task_data: TaskData):
        """Process a task and create it in the appropriate service."""
        # Create the appropriate item based on task type
        google_id = None
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

        # Save to local database
        save_task_to_db(user_id, message, task_data, google_id)

        # Format the time for display
        time_str = f" at {task_data.time}" if task_data.time else ""

        # Prepare response message
        if google_id:
            response = (
                f"{confirmation}! 👍\n"
                f"Title: {task_data.title}\n"
                f"When: {task_data.date}{time_str}\n"
                f"Type: {task_data.task_type.capitalize()}"
            )
        else:
            response = (
                f"I understood your request, but couldn't create the {task_data.task_type} "
                f"in Google. I've saved it locally and will retry later."
            )
        logger.debug(f"Response message: {response}")
        return response
