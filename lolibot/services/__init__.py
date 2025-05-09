from dataclasses import dataclass
from enum import Enum


class StatusType(Enum):
    """Enum for status types."""

    OK = "ok"
    ERROR = "error"
    INFO = "info"


@dataclass(frozen=True)
class StatusItem:
    name: str
    status_type: StatusType


@dataclass(frozen=True)
class TaskData:
    """Data structure for task information."""

    task_type: str
    title: str
    description: str
    date: str
    time: str

    @staticmethod
    def from_dict(data: dict) -> "TaskData":
        """Create a TaskData instance from a dictionary."""
        return TaskData(
            task_type=data.get("task_type"),
            title=data.get("title"),
            description=data.get("description"),
            date=data.get("date"),
            time=data.get("time"),
        )
