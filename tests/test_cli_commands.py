from unittest.mock import patch
from click.testing import CliRunner
from lolibot.cli.commands import apunta_command, change_context_command
from lolibot.config import BotConfig
from lolibot.services import TaskData, TaskResponse


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

    updated = BotConfig.from_file(multi_contexts_config.config_path)
    assert updated.current_context == "personal"


def test_apunta_command(test_config: BotConfig):
    runner = CliRunner()
    user_message = "Create a task to test the CLI command"

    successful_task = TaskData.from_dict({"task_type": "task", "title": "test the CLI command", "description": "This is a test task"})
    processor_patch = patch(
        "lolibot.services.processor.process_user_message",
        autospec=True,
        return_value=[TaskResponse(processed=True, feedback=None, task=successful_task)],
    )
    with processor_patch:
        result = runner.invoke(apunta_command, [user_message], obj={"config": test_config})

    # Check the output
    assert result.exit_code == 0
    assert "Task created 👍" in result.output
    assert "test the CLI command" in result.output
    assert "Invitees" not in result.output
