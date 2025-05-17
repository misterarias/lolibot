from dataclasses import dataclass
from lolibot.config import BotConfig
from lolibot.llm.processor import LLMProcessor
from lolibot.services.middleware.not_task import NotTaskMiddleWare
from lolibot.services.task_manager import TaskData, TaskManager
from lolibot.services.middleware import (
    MiddlewarePipeline,
    JustMeInviteeMiddleware,
    DateValidationMiddleware,
    TitlePrefixTruncateMiddleware,
)


@dataclass
class TaskResponse:
    task: TaskData
    processed: bool = False


def process_user_message(config: BotConfig, user_message: str) -> TaskResponse:
    """
    Process user input to extract task information using LLM providers.
    """
    task_manager = TaskManager(config)

    # Extract task information using LLM
    task_data = LLMProcessor(config).process_text(user_message)

    pipeline = MiddlewarePipeline(
        [
            DateValidationMiddleware(),
            TitlePrefixTruncateMiddleware(config.bot_name),
            JustMeInviteeMiddleware(getattr(config, "default_invitees", [])),
            NotTaskMiddleWare(),
        ]
    )
    processed_data = pipeline.process(user_message, TaskData.from_dict(task_data))

    # Process the task and get response
    task_processed_ok = task_manager.process_task(processed_data)
    return TaskResponse(task=processed_data, processed=task_processed_ok)
