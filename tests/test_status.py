from unittest.mock import MagicMock, patch
from lolibot.services.status import status_service, StatusType
from lolibot.config import BotConfig


def test_status_service_types(provider_factory, test_config: BotConfig):
    google_services_mock = patch("lolibot.services.status.get_google_service", autospec=True)
    google_services_mock.return_value = lambda c, s: type(
        "S",
        (),
        {
            "events": lambda self: type("E", (), {"list": lambda self, **k: type("R", (), {"execute": lambda self: {}})()})(),
            "tasklists": lambda self: type(
                "T", (), {"list": lambda self, **k: type("R", (), {"execute": lambda self: {"items": [{}]}})()}
            )(),
        },
    )()

    # Patch LLMProcessor and get_google_service to always OK
    providers_mock = MagicMock()
    providers_mock.providers = [
        provider_factory(True, True),  # OK
        provider_factory(True, False),  # KO
        provider_factory(False, True),  # Warning
        provider_factory(False, False),  # Warning
    ]
    llm_procesor_mock = patch("lolibot.services.status.LLMProcessor", autospec=True, return_value=providers_mock)
    with llm_procesor_mock, google_services_mock:
        items = status_service(test_config)

    assert len([i for i in items if i.status_type == StatusType.INFO]) == 3
    assert len([i for i in items if i.status_type == StatusType.OK]) == 3
    assert len([i for i in items if i.status_type == StatusType.WARNING]) == 2
    assert len([i for i in items if i.status_type == StatusType.ERROR]) == 1
