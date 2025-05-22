from pathlib import Path

import pytest
from lolibot.config import BotConfig, change_context, load_config


def test_bot_config_initialization(test_config: BotConfig):
    config = test_config
    assert config.bot_name == "TestBot"
    assert config.default_timezone == "UTC"
    assert config.current_context == "default"
    assert config.openai_api_key == "test_openai_key"
    assert config.gemini_api_key == "test_gemini_key"
    assert config.claude_api_key == "test_claude_key"
    assert config.available_contexts == []
    assert config.get_creds_path() == Path(".creds") / "default"


def test_load_config_with_context(tmp_path):
    # Assuming the config.toml file exists in the current directory
    config_path = tmp_path / "config.toml"
    with open(config_path, "w") as f:
        f.write(
            """
            bot_name = "TestBot"
            default_timezone = "UTC"
            current_context = "test_context"
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
    assert config.current_context == "test_context"
    assert config.openai_api_key == "test_openai_key"
    assert config.gemini_api_key == "test_gemini_key"
    assert config.claude_api_key == "test_claude_key"
    assert config.available_contexts == ["test_context"]
    assert config.get_creds_path() == Path(".creds") / "test_context"


def test_default_context_is_invalid(tmp_path):
    # Assuming the config.toml file exists in the current directory
    config_path = tmp_path / "config.toml"
    with open(config_path, "w") as f:
        f.write(
            """
            bot_name = "TestBot"
            default_timezone = "UTC"
            openai_api_key = "default_openai_key"

            [context.default]
            openai_api_key = "test_openai_key"
            """
        )

    with pytest.raises(ValueError) as error:
        load_config(config_path)
    assert str(error.value) == "Context 'default' is not allowed as a explicit configuration context."


def test_change_context(tmp_path):
    config_path = tmp_path / "config.toml"
    with open(config_path, "w") as f:
        f.write(
            """
            bot_name = "TestBot"
            default_timezone = "UTC"
            current_context = "personal"
            openai_api_key = "default_openai_key"
            gemini_api_key = "default_gemini_key"

            [context.personal]
            openai_api_key = "personal_openai_key"
            gemini_api_key = "personal_gemini_key"

            [context.test_context]
            openai_api_key = "test_openai_key"
            """
        )
    current_config = load_config(config_path)
    assert current_config.current_context == "personal"
    assert current_config.available_contexts == ["personal", "test_context"]
    assert current_config.openai_api_key == "personal_openai_key"
    assert current_config.gemini_api_key == "personal_gemini_key"

    # Change context to "test_context"
    change_context("test_context", current_config)

    loaded_config = load_config(config_path)
    assert loaded_config.current_context == "test_context"
    assert loaded_config.openai_api_key == "test_openai_key"
    assert loaded_config.gemini_api_key == "default_gemini_key"

    # Change back to 'personal'
    change_context("personal", current_config)
    assert current_config.current_context == "personal"
    assert current_config.openai_api_key == "personal_openai_key"
    assert current_config.gemini_api_key == "personal_gemini_key"

    # Change context to an invalid context results in error
    with pytest.raises(ValueError) as error:
        change_context("invalid_context", current_config)
    assert str(error.value) == "Context 'invalid_context' not found in available contexts."
