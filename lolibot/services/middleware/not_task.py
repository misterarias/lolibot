import logging

from lolibot.services import TaskData


class NotTaskMiddleWare:
    """
    Middleware to check if a task should be an event.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process(self, message: str, data: TaskData) -> TaskData:
        if data.task_type == "event":
            self.logger.debug("Task is an event, skipping middleware.")
            return data

        if data.time is not None and data.date is not None:
            self.logger.warning("Task has time and date, converting to event.")
            data.task_type = "event"

        return data
