import pytest
from unittest.mock import patch
from lolibot.services.task_manager import TaskManager
from lolibot.services import TaskData, UnknownTaskException


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
def test_process_task_creates_task(mock_create, config):
    tm = TaskManager(config)
    data = TaskData(
        task_type="task",
        title="Test",
        description="desc",
        date="2099-01-01",
        time=None,
        invitees=None,
    )
    resp = tm.process_task(data)
    assert resp is True
    assert mock_create.called


def test_process_invalid_task_type(config):
    tm = TaskManager(config)
    data = TaskData(
        task_type="reminder",
        title="Remind",
        description="desc",
        date="2099-01-01",
        time="09:00",
        invitees=None,
    )
    with pytest.raises(UnknownTaskException):
        tm.process_task(data)


@patch("lolibot.services.task_manager.create_task", return_value=None)
def test_process_task_google_fail(mock_create, config):
    tm = TaskManager(config)
    data = TaskData(
        task_type="task",
        title="Test",
        description="desc",
        date="2099-01-01",
        time=None,
        invitees=None,
    )
    resp = tm.process_task(data)
    assert resp is False
    assert mock_create.called
