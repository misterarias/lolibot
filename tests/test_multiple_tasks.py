"""Tests for multiple task processing functionality."""

import pytest
from unittest.mock import patch

from lolibot import UserMessage
from lolibot.services.processor import TaskResponse, process_user_message


@pytest.fixture
def day_in_the_future():
    """Fixture to provide a date in the future for testing."""
    from datetime import datetime, timedelta

    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


@pytest.fixture
def config():
    class DummyConfig:
        bot_name = "TestBot"
        default_invitees = ["alice@example.com"]
        contact_aliases = {"bob": "bob@example.com"}
        context_name = "default"
        default_timezone = "UTC"
        openai_api_key = "key"
        gemini_api_key = "key"
        claude_api_key = "key"
        telegram_bot_token = "token"
        available_contexts = ["default"]
        config_path = None

    return DummyConfig()


def test_multiple_tasks_success(config, day_in_the_future):
    patch_llm = patch(
        "lolibot.llm.processor.LLMProcessor.process_text",
        side_effect=[
            {"task_type": "task", "title": "Task 1", "description": "D1", "date": day_in_the_future, "time": None, "invitees": None},
            {"task_type": "task", "title": "Task 2", "description": "D2", "date": day_in_the_future, "time": None, "invitees": None},
        ],
    )

    # Set up mock task processing
    patch_process = patch("lolibot.services.task_manager.TaskManager.process_task", autospec=True, side_effect=[True, True])
    user_message = UserMessage(message="Do something first and then do something else", user_id="test_user")

    with patch_llm, patch_process:
        response = process_user_message(config, user_message)

    assert isinstance(response, list)
    assert isinstance(response[0], TaskResponse)
    assert len(response) == 2
    assert all(r.processed for r in response)


def test_multiple_tasks_partial_failure(config, day_in_the_future):
    patch_llm = patch(
        "lolibot.llm.processor.LLMProcessor.process_text",
        side_effect=[
            {"task_type": "task", "title": "Task 1", "description": "D1", "date": day_in_the_future, "time": None, "invitees": None},
            {"task_type": "task", "title": "Task 2", "description": "D2", "date": day_in_the_future, "time": None, "invitees": None},
        ],
    )

    # Set up mock task processing where one task fails
    patch_process = patch("lolibot.services.task_manager.TaskManager.process_task", autospec=True, side_effect=[True, False])

    user_message = UserMessage(message="Do something first and then do something else", user_id="test_user")
    with patch_llm, patch_process:
        response = process_user_message(config, user_message)

    assert isinstance(response, list)
    assert isinstance(response[0], TaskResponse)
    assert len(response) == 2
    assert response[0].processed is True
    assert response[1].processed is False
