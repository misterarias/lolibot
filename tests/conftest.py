"""Pytest configuration file."""

import random
import pytest
import logging

from lolibot.config import BotConfig
from lolibot.llm.base import LLMProvider
from lolibot.llm.default import DefaultProvider


@pytest.fixture
def bot_config(tmp_path):
    config_path = tmp_path / "bot_config.toml"
    with open(config_path, "w") as f:
        f.write(
            """
            bot_name = "TestBot"
            default_timezone = "UTC"
            telegram_feedback_chat_id = "123456"
            current_context = "work"
            telegram_bot_token = "test-token"


            [context.work]
            openai_api_key = "test_openai_key"
            gemini_api_key = "test_gemini_key"
            claude_api_key = "test_claude_key"
            default_invitees = ["me"]
            """
        )

    return BotConfig.from_file(config_path)


@pytest.fixture
def multi_contexts_config(tmp_path):
    config_path = tmp_path / "contexts_config.toml"
    with open(config_path, "w") as f:
        f.write(
            """
            bot_name = "TestBot"
            default_timezone = "UTC"
            telegram_feedback_chat_id = "123456"
            current_context = "test"

            [context.test]
            openai_api_key = "test_openai_key"

            [context.personal]
            openai_api_key = "personal_openai_key"
            """
        )

    return BotConfig.from_file(config_path)


@pytest.fixture()
def test_config(tmp_path) -> BotConfig:
    config_path = tmp_path / "config.toml"
    with open(config_path, "w") as f:
        f.write(
            """
            bot_name = "TestBot"
            default_timezone = "UTC"
            openai_api_key = "test_openai_key"
            gemini_api_key = "test_gemini_key"
            claude_api_key = "test_claude_key"
            """
        )

    return BotConfig.from_file(config_path)


@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    logging.basicConfig(level=logging.DEBUG)


@pytest.fixture()
def provider(test_config) -> LLMProvider:
    """Create a DefaultProvider instance for testing."""
    return DefaultProvider(test_config)


@pytest.fixture()
def provider_factory() -> LLMProvider:
    def create_provider(connected=True, enabled=True) -> LLMProvider:
        class Dummy(LLMProvider):
            def __init__(self, config: BotConfig):
                pass

            def name(self):
                return f"Dummy-{random.randint(1, 1000)}"

            def process_text(self, text):
                pass

            def check_connection(self):
                return connected

            def enabled(self):
                return enabled

        return Dummy(test_config)

    return create_provider
