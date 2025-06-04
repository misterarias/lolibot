"""Task management module for handling tasks, events, and reminders."""

import logging
from lolibot.config import BotConfig
from lolibot.google_api import create_task, create_calendar_event
from lolibot.services import TaskData, UnknownTaskException

logger = logging.getLogger(__name__)


class TaskManager:
    """Manage tasks, events, and reminders."""

    def __init__(self, config: BotConfig):
        self.config = config

    def process_task(self, task_data: TaskData) -> bool:
        """Process a task and create it in the appropriate service."""
        google_id = None
        logger.info(f"Processing task: {task_data}")
        if task_data.task_type == "task":
            google_id = create_task(self.config, task_data)
        elif task_data.task_type == "event":
            google_id = create_calendar_event(self.config, task_data)
        else:
            raise UnknownTaskException(f"Unknown task type: {task_data.task_type}")

        return google_id is not None
