from click.testing import CliRunner
from lolibot.cli.commands import change_context_command
from lolibot.config import load_config


def test_change_context(test_config):
    runner = CliRunner()

    assert test_config.context_name == "test"
    assert test_config.available_contexts == ["default", "test"]

    # Should NOT allow switching to 'default' if more than one context exists
    result = runner.invoke(change_context_command, ["default"], obj={"config": test_config})
    assert result.exit_code == 0  # click always returns 0 unless sys.exit is called
    assert "Context 'default' not found in available contexts." in result.output

    # Should allow switching to 'test'
    result2 = runner.invoke(change_context_command, ["test"], obj={"config": test_config})
    assert result2.exit_code == 0
    assert "Context changed to 'test'" in result2.output

    updated = load_config(test_config.config_path)
    assert updated.context_name == "test"
