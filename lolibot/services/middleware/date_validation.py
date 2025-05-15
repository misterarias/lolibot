from datetime import datetime
from lolibot.services import TaskData


class DateValidationMiddleware:
    def process(self, message: str, data: TaskData) -> TaskData:
        if data.date:
            try:
                task_date = datetime.strptime(data.date, "%Y-%m-%d").date()
                if task_date < datetime.now().date():
                    raise ValueError("Task date cannot be in the past.")
            except ValueError as e:
                raise ValueError(f"Invalid date format: {e}")
        return data
