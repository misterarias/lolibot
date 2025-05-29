from typing import List, Optional
from lolibot.services import TaskData
from lolibot.services.middleware.protocol import TaskMiddleware


class MiddlewarePipeline:
    def __init__(self, middlewares: List[TaskMiddleware]):
        self.middlewares = middlewares

    def process(self, message: str, data: Optional[TaskData] = None) -> TaskData:
        for mw in self.middlewares:
            data = mw.process(message, data)
        return data
