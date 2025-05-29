"""Tests for multiple task processing functionality."""

import pytest
from unittest.mock import patch

from lolibot.services.processor import TaskResponse, split_into_tasks


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


def test_split_task_with_comma():
    text = "Buy milk, call mom, send email"
    segments = split_into_tasks(text)
    assert len(segments) == 3
    assert "Buy milk" in segments
    assert "call mom" in segments
    assert "send email" in segments


def test_split_task_with_spanish_y():
    text = "Comprar leche y llamar a mamá y enviar email"
    segments = split_into_tasks(text)
    assert len(segments) == 3
    assert "Comprar leche" in segments
    assert "llamar a mamá" in segments
    assert "enviar email" in segments


def test_split_task_with_english_and():
    text = "Buy milk and call mom and send email"
    segments = split_into_tasks(text)
    assert len(segments) == 3
    assert "Buy milk" in segments
    assert "call mom" in segments
    assert "send email" in segments


def test_split_task_preserves_time():
    text = "Meeting at 10:30, call mom at 11:15"
    segments = split_into_tasks(text)
    assert len(segments) == 2
    assert "Meeting at 10:30" in segments
    assert "call mom at 11:15" in segments


@patch("lolibot.services.task_manager.TaskManager.process_task")
@patch("lolibot.llm.processor.LLMProcessor.process_text")
def test_multiple_tasks_success(mock_llm, mock_process, config):
    # Set up mock LLM responses
    mock_llm.side_effect = [
        {"task_type": "task", "title": "Task 1", "description": "D1", "date": "2025-06-01", "time": None, "invitees": None},
        {"task_type": "task", "title": "Task 2", "description": "D2", "date": "2025-06-01", "time": None, "invitees": None},
    ]

    # Set up mock task processing
    mock_process.return_value = True

    from lolibot.services.processor import process_user_message

    response = process_user_message(config, "Do something first and then do something else")

    assert isinstance(response, list)
    assert isinstance(response[0], TaskResponse)
    assert len(response) == 2
    assert all(r.processed for r in response)


@patch("lolibot.services.task_manager.TaskManager.process_task")
@patch("lolibot.llm.processor.LLMProcessor.process_text")
def test_multiple_tasks_partial_failure(mock_llm, mock_process, config):
    # Set up mock LLM responses
    mock_llm.side_effect = [
        {"task_type": "task", "title": "Task 1", "description": "D1", "date": "2025-06-01", "time": None, "invitees": None},
        {"task_type": "task", "title": "Task 2", "description": "D2", "date": "2025-06-01", "time": None, "invitees": None},
    ]

    # Set up mock task processing - first succeeds, second fails
    mock_process.side_effect = [True, False]

    from lolibot.services.processor import process_user_message

    response = process_user_message(config, "Do something first and then do something else")

    assert isinstance(response, list)
    assert isinstance(response[0], TaskResponse)
    assert len(response) == 2
    assert response[0].processed is True
    assert response[1].processed is False


def test_support_multilingual_separators():
    text = "Buy milk y call mom, enviar email además " "schedule meeting and send report also create task"
    segments = split_into_tasks(text)
    assert len(segments) == 6  # Fixed: The expected list had 6 items
    expected = ["Buy milk", "call mom", "enviar email", "schedule meeting", "send report", "create task"]
    assert len(expected) == len(segments)
    for task in expected:
        assert any(task in segment for segment in segments)
