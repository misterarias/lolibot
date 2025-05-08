from dataclasses import dataclass
from typing import List

from lolibot.config import BotConfig


from enum import Enum

from lolibot.llm.processor import LLMProcessor


class StatusType(Enum):
    """Enum for status types."""
    OK = "ok"
    ERROR = "error"
    INFO = "info"


@dataclass(frozen=True)
class StatusItem:
    name: str
    status_type: StatusType


def status_service(config: BotConfig) -> List[StatusItem]:
    status_list = [
        StatusItem(f"Bot Name: {config.bot_name}", status_type=StatusType.INFO),
        StatusItem(f"Active context: {config.context_name}", status_type=StatusType.INFO),
    ]

    # Check LLM providers
    llm_processor = LLMProcessor(config)
    for provider in llm_processor.providers:
        if provider.check_connection():
            item = StatusItem(f"{provider.name()} API", status_type=StatusType.OK)
        else:
            item = StatusItem(f"{provider.name()} API", status_type=StatusType.ERROR)
        status_list.append(item)

    # Check Google services
    from ..google_api import get_google_service

    try:
        calendar = get_google_service("calendar")
        calendar.events().list(calendarId="primary", maxResults=1).execute()
        status_list.append(StatusItem("Google Calendar", status_type=StatusType.OK))
    except Exception:
        status_list.append(StatusItem("Google Calendar", status_type=StatusType.KO))

    try:
        tasks = get_google_service("tasks")
        tasks.tasklists().list(maxResults=1).execute()
        status_list.append(StatusItem("Google Tasks", status_type=StatusType.OK))
    except Exception:
        status_list.append(StatusItem("Google Tasks", status_type=StatusType.KO))
    return status_list
