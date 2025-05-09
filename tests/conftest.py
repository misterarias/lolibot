"""Pytest configuration file."""

import pytest
import logging

from lolibot.config import BotConfig, load_config
from lolibot.llm.base import LLMProvider
from lolibot.llm.default import DefaultProvider


@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def test_config(tmp_path) -> BotConfig:
    with open(tmp_path / "test_config.toml", "w") as f:
        f.write(
            """
            [lolibot]
            bot_name = "TestBot"
            default_timezone = "UTC"
            current_context = "test"

            [context.default]
            openai_api_key = "test_openai_key"
            gemini_api_key = "test_gemini_key"
            claude_api_key = "test_claude_key"
            telegram_bot_token = "test_telegram_token"

            [context.test]
            openai_api_key = "test_openai_key_test"
            """
        )
    return load_config(tmp_path / "test_config.toml")


@pytest.fixture
def provider(test_config) -> LLMProvider:
    """Create a DefaultProvider instance for testing."""
    return DefaultProvider(test_config)
