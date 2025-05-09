from pathlib import Path

import pytest
from lolibot.config import BotConfig, change_context, load_config


def test_bot_config_initialization():
    config = BotConfig(
        bot_name="TestBot",
        default_timezone="UTC",
        context_name="default",
        openai_api_key="test_openai_key",
        gemini_api_key="test_gemini_key",
        claude_api_key="test_claude_key",
    )
    assert config.bot_name == "TestBot"
    assert config.default_timezone == "UTC"
    assert config.context_name == "default"
    assert config.openai_api_key == "test_openai_key"
    assert config.gemini_api_key == "test_gemini_key"
    assert config.claude_api_key == "test_claude_key"
    assert config.config_path is None


def test_load_config(tmp_path):
    # Assuming the config.toml file exists in the current directory
    config_path = tmp_path / "config.toml"
    with open(config_path, "w") as f:
        f.write(
            """
            [lolibot]
            bot_name = "TestBot"
            default_timezone = "UTC"
            current_context = "default"

            [context.default]
            openai_api_key = "test_openai_key"
            gemini_api_key = "test_gemini_key"
            claude_api_key = "test_claude_key"
            """
        )

    config = load_config(config_path)
    assert config.bot_name == "TestBot"
    assert config.default_timezone == "UTC"
    assert config.context_name == "default"
    assert config.openai_api_key == "test_openai_key"
    assert config.gemini_api_key == "test_gemini_key"
    assert config.claude_api_key == "test_claude_key"
    assert config.available_contexts == ["default"]
    assert config.get_creds_path() == Path(".creds") / "default"
    assert config.config_path == config_path


def test_load_config_with_context(tmp_path):
    # Assuming the config.toml file exists in the current directory
    config_path = tmp_path / "config.toml"
    with open(config_path, "w") as f:
        f.write(
            """
            [lolibot]
            bot_name = "TestBot"
            default_timezone = "UTC"
            current_context = "test_context"

            [context.default]
            openai_api_key = "default_openai_key"

            [context.test_context]
            openai_api_key = "test_openai_key"
            gemini_api_key = "test_gemini_key"
            claude_api_key = "test_claude_key"
            """
        )

    config = load_config(config_path)
    assert config.bot_name == "TestBot"
    assert config.default_timezone == "UTC"
    assert config.context_name == "test_context"
    assert config.openai_api_key == "test_openai_key"
    assert config.gemini_api_key == "test_gemini_key"
    assert config.claude_api_key == "test_claude_key"
    assert config.available_contexts == ["default", "test_context"]
    assert config.get_creds_path() == Path(".creds") / "test_context"


def test_change_context(tmp_path):
    config_path = tmp_path / "config.toml"
    with open(config_path, "w") as f:
        f.write(
            """
            [lolibot]
            bot_name = "TestBot"
            default_timezone = "UTC"
            current_context = "default"

            [context.default]
            openai_api_key = "default_openai_key"

            [context.test_context]
            openai_api_key = "test_openai_key"
            """
        )
    current_config = load_config(config_path)
    assert current_config.context_name == "default"

    # Change context to "test_context"
    change_context("test_context", current_config)

    loaded_config = load_config(config_path)
    assert loaded_config.context_name == "test_context"

    # Change context to an invalid context results in error
    with pytest.raises(ValueError):
        change_context("invalid_context", current_config)
