import pytest
from unittest.mock import patch
from lolibot.services.task_manager import TaskManager
from lolibot.services import TaskData


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


@patch("lolibot.services.task_manager.create_task", return_value="g123")
@patch("lolibot.services.task_manager.save_task_to_db")
def test_process_task_creates_task(mock_save, mock_create, config):
    tm = TaskManager(config)
    data = TaskData(
        task_type="task",
        title="Test",
        description="desc",
        date="2099-01-01",
        time=None,
        invitees=None,
    )
    resp = tm.process_task("u1", "msg", data)
    assert "Task created" in resp
    assert mock_create.called
    assert mock_save.called


@patch("lolibot.services.task_manager.create_reminder", return_value="r123")
@patch("lolibot.services.task_manager.save_task_to_db")
def test_process_reminder(mock_save, mock_create, config):
    tm = TaskManager(config)
    data = TaskData(
        task_type="reminder",
        title="Remind",
        description="desc",
        date="2099-01-01",
        time="09:00",
        invitees=None,
    )
    resp = tm.process_task("u3", "msg", data)
    assert "Reminder set" in resp
    assert mock_create.called
    assert mock_save.called


@patch("lolibot.services.task_manager.create_task", return_value=None)
@patch("lolibot.services.task_manager.save_task_to_db")
def test_process_task_google_fail(mock_save, mock_create, config):
    tm = TaskManager(config)
    data = TaskData(
        task_type="task",
        title="Test",
        description="desc",
        date="2099-01-01",
        time=None,
        invitees=None,
    )
    resp = tm.process_task("u1", "msg", data)
    assert "couldn't create the task" in resp
    assert mock_create.called
    assert mock_save.called
