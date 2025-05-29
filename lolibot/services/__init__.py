from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


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
    invitees: Optional[List[str]] = None

    @staticmethod
    def from_dict(data: dict) -> "TaskData":
        """Create a TaskData instance from a dictionary."""
        return TaskData(
            task_type=data.get("task_type"),
            title=data.get("title"),
            description=data.get("description"),
            date=data.get("date"),
            time=data.get("time"),
            invitees=data.get("invitees"),
        )


@dataclass
class TaskResponse:
    """Response from processing a task."""

    task: TaskData
    processed: bool = False
    feedback: Optional[str] = None
