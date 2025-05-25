"""Task processing module."""

import re
from dataclasses import dataclass
from typing import List, Set, Optional, Tuple

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
    """Response from processing one or more tasks."""

    tasks: List[TaskData]
    processed: List[bool]
    messages: List[str]

    def has_any_success(self) -> bool:
        """Return True if any task was processed successfully."""
        return any(self.processed)

    def has_any_failure(self) -> bool:
        """Return True if any task failed to process."""
        return not all(self.processed)

    @property
    def task(self) -> Optional[TaskData]:
        """Get first task (for backward compatibility)."""
        return self.tasks[0] if self.tasks else None

    @property
    def is_processed(self) -> bool:
        """Get first task status (for backward compatibility)."""
        return self.processed[0] if self.processed else False


def make_task_key(task: TaskData) -> Tuple[str, Optional[str], Optional[str], str]:
    """Create a unique key for task deduplication."""
    return (task.title.lower(), task.date, task.time, task.task_type)


def normalize_task_separators(text: str) -> str:
    """Convert various task separators to semicolons."""
    # Convert commas followed by word characters
    text = re.sub(r"\s*[,;]\s*(?=\w)", ";", text)

    # Convert Spanish conjunctions
    text = re.sub(r"\s+y\s+(?=\w)", ";", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+además\s+(?=\w)", ";", text, flags=re.IGNORECASE)

    # Convert English conjunctions
    text = re.sub(r"\s+and\s+(?=\w)", ";", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+also\s+(?=\w)", ";", text, flags=re.IGNORECASE)

    return text


def split_into_tasks(text: str) -> List[str]:
    """Split input text into potential task segments."""
    text = normalize_task_separators(text)
    segments = []
    current = []

    # Split preserving time expressions (10:30)
    for part in text.split(";"):
        part = part.strip()
        if not part:
            continue

        # Check if this might be part of a time expression
        last = current[-1].strip() if current else ""
        is_prev_num = last.replace(":", "").replace(".", "").isdigit()
        is_curr_num = part.replace(":", "").replace(".", "").isdigit()

        if current and is_prev_num and is_curr_num:
            current.append(part)
        else:
            if current:
                segments.append("".join(current).strip())
            current = [part]

    if current:
        segments.append("".join(current).strip())

    return segments or [text]


def process_task_segment(
    config: BotConfig,
    segment: str,
    llm_processor: LLMProcessor,
    pipeline: MiddlewarePipeline,
    task_manager: TaskManager,
    seen_task_keys: Set[Tuple[str, Optional[str], Optional[str], str]],
) -> Tuple[Optional[TaskData], bool, str]:
    """Process a single task segment."""
    try:
        task_data = llm_processor.process_text(segment)
        processed_data = pipeline.process(segment, TaskData.from_dict(task_data))
        task_key = make_task_key(processed_data)

        if task_key in seen_task_keys:
            msg = f"Skipped duplicate task: {processed_data.title}"
            return None, False, msg

        seen_task_keys.add(task_key)
        task_processed_ok = task_manager.process_task(processed_data)

        msg = f"Successfully created: {processed_data.title}" if task_processed_ok else f"Failed to create: {processed_data.title}"

        return processed_data, task_processed_ok, msg

    except ValueError as e:
        return None, False, f"Error: {str(e)}"
    except Exception as e:
        return None, False, f"Unexpected error: {str(e)}"


def process_user_message(config: BotConfig, user_message: str) -> TaskResponse:
    """Process user input to extract and create tasks."""
    task_manager = TaskManager(config)
    llm_processor = LLMProcessor(config)

    tasks_data = []
    processed_results = []
    feedback_messages = []
    seen_task_keys: Set[Tuple[str, Optional[str], Optional[str], str]] = set()

    # Process each task segment independently
    segments = split_into_tasks(user_message)

    # Initialize pipeline for processing tasks
    pipeline = MiddlewarePipeline(
        [
            DateValidationMiddleware(),
            TitlePrefixTruncateMiddleware(config.bot_name),
            JustMeInviteeMiddleware(getattr(config, "default_invitees", [])),
            NotTaskMiddleWare(),
        ]
    )

    # Process each segment
    for segment in segments:
        task, processed, msg = process_task_segment(
            config=config,
            segment=segment,
            llm_processor=llm_processor,
            pipeline=pipeline,
            task_manager=task_manager,
            seen_task_keys=seen_task_keys,
        )
        if task:
            tasks_data.append(task)
            processed_results.append(processed)
        feedback_messages.append(msg)

    # Create dummy response if no tasks were processed
    if not tasks_data:
        tasks_data = [
            TaskData(
                task_type="task", title="Invalid task", description="No valid tasks could be processed", date=None, time=None, invitees=None
            )
        ]
        processed_results = [False]
        if not feedback_messages:
            msg = "No valid tasks could be processed from the input"
            feedback_messages = [msg]

    return TaskResponse(tasks=tasks_data, processed=processed_results, messages=feedback_messages)
