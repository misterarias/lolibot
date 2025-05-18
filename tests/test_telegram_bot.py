import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from lolibot.telegram import bot as telegram_bot
from lolibot.config import BotConfig


@pytest.fixture
def config():
    return BotConfig(
        bot_name="TestBot",
        default_timezone="UTC",
        context_name="default",
        telegram_feedback_chat_id="123456",
        openai_api_key="test-openai",
        gemini_api_key="test-gemini",
        claude_api_key="test-claude",
        telegram_bot_token="test-token",
        available_contexts=["default", "work"],
        config_path=None,
        default_invitees=["me"],
        contexts={"default": {}, "work": {}},
    )


@pytest.mark.asyncio
async def test_start_command(config):
    update = MagicMock()
    context = MagicMock()
    update.message.reply_text = AsyncMock()
    await telegram_bot.start_command(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_help_command(config):
    update = MagicMock()
    context = MagicMock()
    update.message.reply_text = AsyncMock()
    await telegram_bot.help_command(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_status_command(config):
    update = MagicMock()
    context = MagicMock()
    context.application.bot_data = {"config": config, "start_time": 0}
    update.message.reply_markdown_v2 = AsyncMock()
    with patch("lolibot.services.status.status_service", return_value=[]):
        await telegram_bot.status_command(update, context)
    update.message.reply_markdown_v2.assert_called_once()


@pytest.mark.asyncio
async def test_get_context_command(config):
    update = MagicMock()
    context = MagicMock()
    context.application.bot_data = {"config": config}
    update.message.reply_markdown_v2 = AsyncMock()
    await telegram_bot.get_context_command(update, context)
    update.message.reply_markdown_v2.assert_called_once()


@pytest.mark.asyncio
async def test_set_context_command_success(config):
    update = MagicMock()
    update.message.text = "set_work"
    context = MagicMock()
    context.application.bot_data = {"config": config}
    update.message.reply_text = AsyncMock()
    with patch("lolibot.config.change_context", return_value=config):
        await telegram_bot.set_context_command(update, context)
    update.message.reply_text.assert_called()


@pytest.mark.asyncio
async def test_set_context_command_error(config):
    update = MagicMock()
    update.message.text = "set_invalid"
    context = MagicMock()
    context.application.bot_data = {"config": config}
    update.message.reply_text = AsyncMock()
    with patch("lolibot.config.change_context", side_effect=Exception("fail")):
        await telegram_bot.set_context_command(update, context)
    update.message.reply_text.assert_called()


@pytest.mark.asyncio
async def test_error_handler_with_feedback(config):
    update = MagicMock()
    context = MagicMock()
    context.application.bot_data = {"config": config}
    context.error = Exception("fail")
    context.error.__traceback__ = None
    context.bot.send_message = AsyncMock()
    await telegram_bot.error_handler(update, context)
    context.bot.send_message.assert_called()


@pytest.mark.asyncio
async def test_error_handler_no_feedback(config):
    update = MagicMock()
    context = MagicMock()
    config.telegram_feedback_chat_id = None
    context.application.bot_data = {"config": config}
    context.error = Exception("fail")
    context.error.__traceback__ = None
    context.bot.send_message = AsyncMock()
    await telegram_bot.error_handler(update, context)
    context.bot.send_message.assert_not_called()
