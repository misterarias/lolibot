from lolibot.google_api import create_task, create_calendar_event, create_reminder
from lolibot.config import BotConfig
from lolibot.services import TaskData


def make_config():
    return BotConfig(
        bot_name="TestBot",
        default_timezone="UTC",
        context_name="default",
        openai_api_key="k",
        gemini_api_key="k",
        claude_api_key="k",
        telegram_bot_token="t",
        available_contexts=["default"],
        config_path=None,
    )


def make_task():
    return TaskData(
        task_type="task",
        title="T",
        description="D",
        date="2025-05-15",
        time="10:00",
        invitees=["a@example.com"],
    )


def test_create_task_handles_error(monkeypatch):
    monkeypatch.setattr("lolibot.google_api.get_google_service", lambda *a, **k: (_ for _ in ()).throw(Exception("fail")))
    assert create_task(make_config(), make_task()) is None


def test_create_calendar_event_handles_error(monkeypatch):
    monkeypatch.setattr("lolibot.google_api.get_google_service", lambda *a, **k: (_ for _ in ()).throw(Exception("fail")))
    assert create_calendar_event(make_config(), make_task()) is None


def test_create_reminder_handles_error(monkeypatch):
    monkeypatch.setattr("lolibot.google_api.get_google_service", lambda *a, **k: (_ for _ in ()).throw(Exception("fail")))
    assert create_reminder(make_config(), make_task()) is None
