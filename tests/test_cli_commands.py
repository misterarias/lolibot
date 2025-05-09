from click.testing import CliRunner
from lolibot.cli.commands import change_context_command
from lolibot.config import load_config


def test_change_context(test_config):
    runner = CliRunner()

    assert test_config.context_name == "test"
    assert test_config.available_contexts == ["default", "test"]

    result = runner.invoke(change_context_command, ["default"], obj={"config": test_config})
    assert result.exit_code == 0
    assert "Context changed to 'default'" in result.output

    updated = load_config(test_config.config_path)
    assert updated.context_name == "default"
