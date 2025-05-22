from lolibot.services.status import status_service, StatusType
from lolibot.config import BotConfig


def test_status_service_types(monkeypatch, test_config: BotConfig):
    # Patch LLMProcessor and get_google_service to always OK
    monkeypatch.setattr(
        "lolibot.services.status.LLMProcessor",
        lambda c: type("X", (), {"providers": [type("P", (), {"name": lambda s: "Fake", "check_connection": lambda s: True})()]})(),
    )
    monkeypatch.setattr(
        "lolibot.services.status.get_google_service",
        lambda c, s: type(
            "S",
            (),
            {
                "events": lambda self: type("E", (), {"list": lambda self, **k: type("R", (), {"execute": lambda self: {}})()})(),
                "tasklists": lambda self: type(
                    "T", (), {"list": lambda self, **k: type("R", (), {"execute": lambda self: {"items": [{}]}})()}
                )(),
            },
        )(),
    )
    items = status_service(test_config)
    assert any(i.status_type == StatusType.OK for i in items)
    assert any(i.status_type == StatusType.INFO for i in items)
    assert any(isinstance(i.name, str) for i in items)
