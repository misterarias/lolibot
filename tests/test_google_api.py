from lolibot.google_api import create_task, create_calendar_event
from lolibot.services import TaskData


def make_task():
    return TaskData(
        task_type="task",
        title="T",
        description="D",
        date="2025-05-15",
        time="10:00",
        invitees=["a@example.com"],
    )


def test_create_task_handles_error(monkeypatch, test_config):
    monkeypatch.setattr("lolibot.google_api.get_google_service", lambda *a, **k: (_ for _ in ()).throw(Exception("fail")))
    assert create_task(test_config, make_task()) is None


def test_create_calendar_event_handles_error(monkeypatch, test_config):
    monkeypatch.setattr("lolibot.google_api.get_google_service", lambda *a, **k: (_ for _ in ()).throw(Exception("fail")))
    assert create_calendar_event(test_config, make_task()) is None
