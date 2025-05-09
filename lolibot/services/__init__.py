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
    google_id: str = None
