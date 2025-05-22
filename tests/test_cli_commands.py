from click.testing import CliRunner
from lolibot.cli.commands import change_context_command
from lolibot.config import BotConfig, load_config


def test_change_context(multi_contexts_config: BotConfig):
    runner = CliRunner()

    assert multi_contexts_config.current_context == "test"
    assert multi_contexts_config.available_contexts == ["test", "personal"]

    # Should NOT allow switching to 'default' if more than one context exists
    result = runner.invoke(change_context_command, ["default"], obj={"config": multi_contexts_config})
    assert result.exit_code == 0  # click always returns 0 unless sys.exit is called
    assert "Context 'default' not found in available contexts." in result.output

    # Should allow switching to 'personal'
    result2 = runner.invoke(change_context_command, ["personal"], obj={"config": multi_contexts_config})
    assert result2.exit_code == 0
    assert "Context changed to 'personal'" in result2.output

    updated = load_config(multi_contexts_config.config_path)
    assert updated.current_context == "personal"
