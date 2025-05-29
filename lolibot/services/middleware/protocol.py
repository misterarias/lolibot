from typing import Optional, Protocol
from lolibot.services import TaskData


class TaskMiddleware(Protocol):
    def process(self, message: str, data: Optional[TaskData] = None) -> TaskData: ...
