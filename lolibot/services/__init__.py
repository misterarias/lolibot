from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import List, Optional


class UnknownTaskException(Exception):
    """Exception raised for unknown task types."""

    pass


class StatusType(Enum):
    """Enum for status types."""

    OK = "ok"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


@dataclass(frozen=True)
class StatusItem:
    name: str
    status_type: StatusType


@dataclass(frozen=True)
class TaskData:
    """Data structure for task information."""

    task_type: str
    title: str
    description: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    invitees: Optional[List[str]] = None

    @staticmethod
    def from_error(error_message: str) -> "TaskData":
        """Create a TaskData instance from an error message."""
        now = date.today()
        return TaskData.from_dict(
            {
                "task_type": "error",
                "title": error_message,
                "description": "",
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%s"),
            }
        )

    @staticmethod
    def from_dict(data: dict) -> "TaskData":
        """Create a TaskData instance from a dictionary."""
        return TaskData(
            task_type=data.get("task_type"),
            title=data.get("title"),
            description=data.get("description", None),
            date=data.get("date", None),
            time=data.get("time", None),
            invitees=data.get("invitees", []),
        )


@dataclass
class TaskResponse:
    """Response from processing a task."""

    task: TaskData
    processed: bool = False
    feedback: Optional[str] = None
