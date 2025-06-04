import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from lolibot.services import TaskData
from lolibot.services.processor import TaskResponse
from lolibot.telegram.start_command import command as start_command
from lolibot.telegram.help_command import command as help_command
from lolibot.telegram.status_command import command as status_command
from lolibot.telegram.get_context_command import command as get_context_command
from lolibot.telegram.set_context_command import command as set_context_command
from lolibot.telegram.error_handler import handler as error_handler
from lolibot.telegram.message_handler import handler as message_handler
from lolibot.telegram.bot import run_telegram_bot


def test_bot_start_fails_no_token(test_config):
    """Test that the bot fails to start without a token."""
    config = test_config
    with pytest.raises(SystemExit):
        run_telegram_bot(config)


def test_bot_start_with_good_config(bot_config):
    """Test that the bot starts with a valid config."""
    config = bot_config

    with patch("lolibot.telegram.bot.create_application") as mock_create_app:
        application = MagicMock()
        mock_create_app.return_value = application

        run_telegram_bot(config)

        mock_create_app.assert_called_once_with(config)
        application.add_handler.call_count == 6
        application.add_error_handler.assert_called()
        application.run_polling.assert_called_once()


@pytest.mark.asyncio
async def test_start_command(bot_config):
    update = MagicMock()
    context = MagicMock()
    update.message.reply_text = AsyncMock()
    await start_command(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_help_command(bot_config):
    update = MagicMock()
    context = MagicMock()
    update.message.reply_text = AsyncMock()
    await help_command(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_status_command(bot_config, provider_factory):
    update = MagicMock()
    context = MagicMock()
    context.application.bot_data = {"config": bot_config, "start_time": time.time() - 1}
    update.message.reply_markdown_v2 = AsyncMock()

    # TODO - mock google services
    google_services_mock = patch("lolibot.services.status.get_google_service", autospec=True)
    google_services_mock.return_value = lambda c, s: type(
        "S",
        (),
        {
            "events": lambda self: type("E", (), {"list": lambda self, **k: type("R", (), {"execute": lambda self: {}})()})(),
            "tasklists": lambda self: type(
                "T", (), {"list": lambda self, **k: type("R", (), {"execute": lambda self: {"items": [{}]}})()}
            )(),
        },
    )()

    # Patch LLMProcessor and get_google_service to always OK
    providers_mock = MagicMock()
    providers_mock.providers = [
        provider_factory(True, True),  # OK
        provider_factory(True, False),  # KO
        provider_factory(False, True),  # Warning
        provider_factory(False, False),  # Warning
    ]
    llm_procesor_mock = patch("lolibot.services.status.LLMProcessor", autospec=True, return_value=providers_mock)

    with llm_procesor_mock, google_services_mock:
        await status_command(update, context)
    update.message.reply_markdown_v2.assert_called_once()
    status_message = update.message.reply_markdown_v2.call_args[0][0]
    assert "Uptime: 0h 0m 1s" in status_message
    assert "❌ " in status_message
    assert "✅ " in status_message
    assert "⚠️ " in status_message


@pytest.mark.asyncio
async def test_get_context_command(bot_config):
    update = MagicMock()
    context = MagicMock()
    context.application.bot_data = {"config": bot_config}
    update.message.reply_markdown_v2 = AsyncMock()
    await get_context_command(update, context)
    update.message.reply_markdown_v2.assert_called_once()


@pytest.mark.asyncio
async def test_set_context_command_success(bot_config):
    update = MagicMock()
    update.message.text = "set_work"
    context = MagicMock()
    context.application.bot_data = {"config": bot_config}
    update.message.reply_text = AsyncMock()
    await set_context_command(update, context)
    update.message.reply_text.assert_called()


@pytest.mark.asyncio
async def test_set_context_command_error(bot_config):
    update = MagicMock()
    update.message.text = "set_invalid"
    context = MagicMock()
    context.application.bot_data = {"config": bot_config}
    update.message.reply_text = AsyncMock()
    await set_context_command(update, context)
    update.message.reply_text.assert_called()


@pytest.mark.asyncio
async def test_error_handler_with_feedback(bot_config):
    update = MagicMock()
    context = MagicMock()
    context.application.bot_data = {"config": bot_config}
    context.error = Exception("fail")
    context.error.__traceback__ = None
    context.bot.send_message = AsyncMock()
    await error_handler(update, context)
    context.bot.send_message.assert_called()


@pytest.mark.asyncio
async def test_error_handler_no_feedback(test_config):
    update = MagicMock()
    context = MagicMock()

    context.application.bot_data = {"config": test_config}
    context.error = Exception("fail")
    context.error.__traceback__ = None
    context.bot.send_message = AsyncMock()
    await error_handler(update, context)
    context.bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_message_handler_multi_task_success(bot_config):
    update = MagicMock()
    context = MagicMock()
    context.application.bot_data = {"config": bot_config}
    update.message.text = "do task1 and task2"
    update.message.reply_markdown_v2 = AsyncMock()
    update.message.reply_text = AsyncMock()

    # Simulate successful multi-task response
    tasks = [
        TaskData(task_type="task", title="Task1", description="desc1", date="2025-05-23", time="12:00", invitees=["me"]),
        TaskData(task_type="task", title="Task2", description="desc2", date="2025-05-23", time="14:00", invitees=None),
    ]
    messages = ["Successfully created: Task1", "Successfully created: Task2"]
    task_responses = [
        TaskResponse(task=tasks[0], processed=True, feedback=messages[0]),
        TaskResponse(task=tasks[1], processed=True, feedback=messages[1]),
    ]

    mock_process = patch("lolibot.telegram.message_handler.process_user_message", return_value=task_responses)
    with mock_process:
        await message_handler(update, context)

    assert update.message.reply_markdown_v2.call_count == 3


@pytest.mark.asyncio
async def test_message_handler_fallback(bot_config):
    update = MagicMock()
    context = MagicMock()
    context.application.bot_data = {"config": bot_config}
    update.message.text = "do task1 and task2"
    update.message.reply_markdown_v2 = AsyncMock(side_effect=Exception("fail"))
    update.message.reply_text = AsyncMock()

    task = TaskData(task_type="task", title="Task1", description="desc1", date="2025-05-23", time="12:00", invitees=["me"])
    message = "Successfully created: Task1"
    task_responses = [TaskResponse(task=task, processed=True, feedback=message)]

    # Mock process and save
    mock_process = patch("lolibot.telegram.message_handler.process_user_message", return_value=task_responses)
    with mock_process:
        await message_handler(update, context)

    assert update.message.reply_markdown_v2.call_count == 2
    assert update.message.reply_text.call_count == 2


@pytest.mark.asyncio
async def test_message_handler_with_failed_tasks(bot_config):
    update = MagicMock()
    context = MagicMock()
    context.application.bot_data = {"config": bot_config}
    update.message.text = "do task1, invalid task and duplicate task1"
    update.message.reply_markdown_v2 = AsyncMock()
    update.message.reply_text = AsyncMock()

    messages = ["Successfully created: Task1", "Error: Invalid date format", "Skipped duplicate task: Task1"]
    task_responses = [
        TaskResponse(
            task=TaskData(task_type="task", title="Task1", description="desc1", date="2025-05-23", time="12:00", invitees=["me"]),
            processed=True,
            feedback=messages[0],
        ),
        TaskResponse(task=None, processed=False, feedback=messages[1]),
        TaskResponse(task=None, processed=False, feedback=messages[2]),
    ]

    mock_process = patch("lolibot.telegram.message_handler.process_user_message", return_value=task_responses)
    with mock_process:
        await message_handler(update, context)

    assert update.message.reply_markdown_v2.call_count == 4
    update.message.reply_text.assert_not_called()

    # Verify the response includes failure messages
    response = " ".join(c[0][0] for c in update.message.reply_markdown_v2.await_args_list)
    assert "Processed 1/3 tasks" in response
    assert "✅ Task1" in response
    assert "❌ Error: Invalid date format" in response
    assert "❌ Skipped duplicate task" in response
