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
async def test_status_command(bot_config):
    update = MagicMock()
    context = MagicMock()
    context.application.bot_data = {"config": bot_config, "start_time": 0}
    update.message.reply_markdown_v2 = AsyncMock()
    with patch("lolibot.services.status.status_service", return_value=[]):
        await status_command(update, context)
    update.message.reply_markdown_v2.assert_called_once()


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
async def test_message_handler_success(bot_config):
    update = MagicMock()
    context = MagicMock()
    context.application.bot_data = {"config": bot_config}
    update.message.text = "do something"
    update.message.reply_markdown_v2 = AsyncMock()
    update.message.reply_text = AsyncMock()

    # Simulate a successful task response
    task = TaskData(task_type="task", title="Test", description="desc", date="2025-05-23", time="12:00", invitees=["me"])
    task_response = TaskResponse(task=task, processed=True)
    with (
        patch("lolibot.telegram.message_handler.process_user_message", return_value=task_response),
        patch("lolibot.telegram.message_handler.save_task_to_db"),
    ):
        await message_handler(update, context)

    update.message.reply_markdown_v2.assert_called_once()
    update.message.reply_text.assert_not_called()


@pytest.mark.asyncio
async def test_message_handler_fallback(bot_config):
    update = MagicMock()
    context = MagicMock()
    context.application.bot_data = {"config": bot_config}
    update.message.text = "do something"
    update.message.reply_markdown_v2 = AsyncMock(side_effect=Exception("fail"))
    update.message.reply_text = AsyncMock()
    # Simulate a successful task response
    task = TaskData(task_type="task", title="Test", description="desc", date="2025-05-23", time="12:00", invitees=["me"])
    task_response = TaskResponse(task=task, processed=True)
    with (
        patch("lolibot.telegram.message_handler.process_user_message", return_value=task_response),
        patch("lolibot.telegram.message_handler.save_task_to_db"),
    ):
        await message_handler(update, context)
    update.message.reply_markdown_v2.assert_called_once()
    update.message.reply_text.assert_called_once()
