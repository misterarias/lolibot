from pathlib import Path

import pytest
from lolibot.config import BotConfig


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


def test_save_config(tmp_path):
    config_path = tmp_path / "config.toml"
    with open(config_path, "w") as f:
        f.write(
            """
            bot_name = "TestBot"
            default_timezone = "UTC"
            current_context = "work"
            openai_api_key = "test_openai_key"
            gemini_api_key = "test_gemini_key"
            claude_api_key = "test_claude_key"

            [context.work]
            openai_api_key = "work_openai_key"

            [context.personal]
            gemini_api_key = "personal_gemini_key"
            openai_api_key = "personal_openai_key"
            """
        )

    config = BotConfig.from_file(config_path)
    assert config.bot_name == "TestBot"
    assert config.default_timezone == "UTC"
    assert config.current_context == "work"
    assert config.openai_api_key == "work_openai_key"
    assert config.gemini_api_key == "test_gemini_key"
    assert config.claude_api_key == "test_claude_key"

    # Save the configuration
    config.to_file()

    # Load the configuration again to verify it was saved correctly
    loaded_config = BotConfig.from_file(config_path)
    assert loaded_config.bot_name == "TestBot"
    assert loaded_config.default_timezone == "UTC"
    assert loaded_config.current_context == "work"
    assert loaded_config.available_contexts == ["work", "personal"]
    assert loaded_config.openai_api_key == "work_openai_key"
    assert loaded_config.gemini_api_key == "test_gemini_key"
    assert loaded_config.claude_api_key == "test_claude_key"


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

    config = BotConfig.from_file(config_path)
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
        BotConfig.from_file(config_path)
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
    current_config = BotConfig.from_file(config_path)
    assert current_config.current_context == "personal"
    assert current_config.available_contexts == ["personal", "test_context"]
    assert current_config.openai_api_key == "personal_openai_key"
    assert current_config.gemini_api_key == "personal_gemini_key"

    # Change context to "test_context"
    current_config.change_context("test_context")

    loaded_config = BotConfig.from_file(config_path)
    assert loaded_config.current_context == "test_context"
    assert loaded_config.openai_api_key == "test_openai_key"
    assert loaded_config.gemini_api_key == "default_gemini_key"

    # Change back to 'personal'
    current_config.change_context("personal")
    assert current_config.current_context == "personal"
    assert current_config.openai_api_key == "personal_openai_key"
    assert current_config.gemini_api_key == "personal_gemini_key"

    # Change context to an invalid context results in error
    with pytest.raises(ValueError) as error:
        current_config.change_context("invalid_context")
    assert str(error.value) == "Context 'invalid_context' not found in available contexts."
