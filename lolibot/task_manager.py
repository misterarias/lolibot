"""Task management module for handling tasks, events, and reminders."""
from lolibot.config import logger
from lolibot.google_api import create_task, create_calendar_event, create_reminder
from lolibot.db import save_task_to_db


class TaskManager:
    """Manage tasks, events, and reminders."""

    @staticmethod
    def create_task(task_data):
        """Create a task in Google Tasks."""
        return create_task(task_data)

    @staticmethod
    def create_calendar_event(event_data):
        """Create an event in Google Calendar."""
        return create_calendar_event(event_data)

    @staticmethod
    def create_reminder(reminder_data):
        """Create a reminder in Google Calendar."""
        return create_reminder(reminder_data)

    @staticmethod
    def save_to_db(user_id, message, task_data, google_id=None):
        """Save task information to the local database."""
        save_task_to_db(user_id, message, task_data, google_id)

    @staticmethod
    def process_task(user_id, message, task_data):
        """Process a task and create it in the appropriate service."""
        # Create the appropriate item based on task type
        google_id = None
        if task_data["task_type"] == "task":
            google_id = TaskManager.create_task(task_data)
            confirmation = "Task created"
        elif task_data["task_type"] == "event":
            google_id = TaskManager.create_calendar_event(task_data)
            confirmation = "Calendar event created"
        elif task_data["task_type"] == "reminder":
            google_id = TaskManager.create_reminder(task_data)
            confirmation = "Reminder set"

        # Save to local database
        TaskManager.save_to_db(user_id, message, task_data, google_id)

        # Format the time for display
        time_str = f" at {task_data['time']}" if task_data["time"] else ""

        # Prepare response message
        if google_id:
            response = (
                f"{confirmation}! 👍\n"
                f"Title: {task_data['title']}\n"
                f"When: {task_data['date']}{time_str}\n"
                f"Type: {task_data['task_type'].capitalize()}"
            )
        else:
            response = (
                f"I understood your request, but couldn't create the {task_data['task_type']} "
                f"in Google. I've saved it locally and will retry later."
            )
        logger.debug(f"Response message: {response}")
        return response
