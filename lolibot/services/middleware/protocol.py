from typing import Protocol
from lolibot.services import TaskData


class TaskMiddleware(Protocol):
    def process(self, message: str, data: TaskData) -> TaskData: ...
