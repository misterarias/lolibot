from lolibot.services.status import status_service, StatusType
from lolibot.config import BotConfig


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


def test_status_service_types(monkeypatch):
    config = make_config()
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
    items = status_service(config)
    assert any(i.status_type == StatusType.OK for i in items)
    assert any(i.status_type == StatusType.INFO for i in items)
    assert any(isinstance(i.name, str) for i in items)
