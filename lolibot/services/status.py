from typing import List

from lolibot.config import BotConfig


from lolibot.google_api import get_google_service
from lolibot.llm.processor import LLMProcessor
from lolibot.services import StatusItem, StatusType


def status_service(config: BotConfig) -> List[StatusItem]:
    status_list = [
        StatusItem(f"Bot Name        {config.bot_name}", status_type=StatusType.INFO),
        StatusItem(f"Bot version     {config.version}", status_type=StatusType.INFO),
        StatusItem(f"Active context  {config.current_context}", status_type=StatusType.INFO),
    ]

    # Check LLM providers
    llm_processor = LLMProcessor(config)
    for provider in llm_processor.providers:
        if not provider.enabled():
            item = StatusItem(f"{provider.name()} DISABLED", status_type=StatusType.WARNING)
        elif provider.check_connection():
            item = StatusItem(f"{provider.name()} API", status_type=StatusType.OK)
        else:
            item = StatusItem(f"{provider.name()} API", status_type=StatusType.ERROR)
        status_list.append(item)

    try:
        calendar = get_google_service(config, "calendar")
        calendar.events().list(calendarId="primary", maxResults=1).execute()
        status_list.append(StatusItem("Google Calendar API", status_type=StatusType.OK))
    except Exception:
        status_list.append(StatusItem("Google Calendar API", status_type=StatusType.ERROR))

    try:
        tasks = get_google_service(config, "tasks")
        tasks.tasklists().list(maxResults=1).execute()
        status_list.append(StatusItem("Google Tasks API", status_type=StatusType.OK))
    except Exception:
        status_list.append(StatusItem("Google Tasks API", status_type=StatusType.ERROR))
    return status_list
