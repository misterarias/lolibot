"""Tests for the main application module."""

import logging
import pytest
from click.testing import CliRunner
from app import configure_logging, main


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary config file for testing."""
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
    return config_path


def test_logging_configuration():
    """Test that logging is properly configured at different verbosity levels."""
    # Test warning level (default)
    configure_logging(0)
    assert logging.getLogger().getEffectiveLevel() == logging.WARNING
    assert logging.getLogger("telegram.ext").getEffectiveLevel() == logging.WARNING

    # Test info level
    configure_logging(1)
    assert logging.getLogger().getEffectiveLevel() == logging.INFO

    # Test debug level
    configure_logging(2)
    assert logging.getLogger().getEffectiveLevel() == logging.DEBUG


def test_cli_commands_registered():
    """Test that all CLI commands are properly registered."""
    command_names = [cmd.name for cmd in main.commands.values()]
    assert "apunta" in command_names
    assert "telegram" in command_names
    assert "status" in command_names
    assert "set-context" in command_names


def test_main_help(cli_runner):
    """Test that the main help text is displayed."""
    result = cli_runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Task Manager" in result.output
    assert "--config-path" in result.output
    assert "--verbose" in result.output


@pytest.mark.slow
def test_main_with_config(cli_runner, temp_config, monkeypatch):
    """Test main command with config file."""
    monkeypatch.setattr("builtins.print", lambda x: None)  # Suppress print output

    result = cli_runner.invoke(main, ["--config-path", str(temp_config), "status"])
    assert result.exit_code == 0


def test_main_invalid_config(cli_runner, tmp_path):
    """Test main command with invalid config path."""
    invalid_config = tmp_path / "nonexistent.toml"
    result = cli_runner.invoke(main, ["--config-path", str(invalid_config)])
    assert result.exit_code == 2  # Click's error code for invalid parameter
    assert "does not exist" in result.output


@pytest.mark.slow
def test_verbosity_levels(cli_runner, temp_config):
    """Test different verbosity levels."""
    # Test with increasing verbosity
    for v_count in range(4):
        v_args = ["-" + "v" * v_count] if v_count > 0 else []
        result = cli_runner.invoke(main, ["--config-path", str(temp_config), *v_args, "status"])
        assert result.exit_code == 0
