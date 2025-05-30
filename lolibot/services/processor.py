"""Task processing module."""

import logging
import re
from typing import List

from lolibot import UserMessage
from lolibot.config import BotConfig
from lolibot.db import save_task_to_db
from lolibot.llm.processor import LLMProcessor
from lolibot.services import TaskResponse
from lolibot.services.middleware.not_task import NotTaskMiddleWare
from lolibot.services.middleware.test_message_check import TestCheckerMiddleware
from lolibot.services.task_manager import TaskData, TaskManager
from lolibot.services.middleware import (
    MiddlewarePipeline,
    JustMeInviteeMiddleware,
    DateValidationMiddleware,
    TitlePrefixTruncateMiddleware,
)

logger = logging.getLogger(__name__)


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
    segment: str,
    llm_processor: LLMProcessor,
    pipeline: MiddlewarePipeline,
    task_manager: TaskManager,
) -> TaskResponse:
    """Process a single task segment."""
    try:
        raw_task_data = llm_processor.process_text(segment)
        task_data = TaskData.from_dict(raw_task_data)
        processed_data = pipeline.process(segment, task_data)
        task_processed_ok = task_manager.process_task(processed_data)

        msg = f"Successfully created: {processed_data.title}" if task_processed_ok else f"Failed to create: {processed_data.title}"
        task_response = TaskResponse(task=task_data, processed=task_processed_ok, feedback=msg)

        return task_response

    except ValueError as e:
        error_msg = f"Middleware error processing {segment}: {str(e)}"
    except Exception as e:
        error_msg = f"Unexpected error processing {segment}: {str(e)}"

    error_task = TaskData.from_error(error_msg)
    return TaskResponse(task=error_task, processed=False, feedback=error_msg)


def process_user_message(config: BotConfig, user_message: UserMessage) -> List[TaskResponse]:
    """Process user input to extract and create tasks."""
    task_manager = TaskManager(config)
    llm_processor = LLMProcessor(config)
    task_responses = []

    # Process each task segment independently
    segments = split_into_tasks(user_message.message)

    # Initialize pipeline for cleaning tasks
    pre_work_pipeline = MiddlewarePipeline([TestCheckerMiddleware()])

    # Initialize pipeline for processed tasks
    processed_tasks_pipeline = MiddlewarePipeline(
        [
            DateValidationMiddleware(),
            TitlePrefixTruncateMiddleware(config.bot_name),
            JustMeInviteeMiddleware(getattr(config, "default_invitees", [])),
            NotTaskMiddleWare(),
        ]
    )

    # Process each segment
    for segment in segments:
        try:
            pre_work_pipeline.process(segment)
            task_response = process_task_segment(
                segment=segment, llm_processor=llm_processor, pipeline=processed_tasks_pipeline, task_manager=task_manager
            )
        except ValueError as e:
            msg = f"Text '{segment}' is invalid: {e}"
            logger.info(msg)
            task_data = TaskData.from_error(msg)
            task_response = TaskResponse(task=task_data, processed=False, feedback=msg)

        # Store info in the database for each task and append
        save_task_to_db(user_message.user_id, segment, task_response=task_response)
        task_responses.append(task_response)

    return task_responses
