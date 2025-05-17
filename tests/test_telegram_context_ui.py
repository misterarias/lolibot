import pytest
from unittest.mock import AsyncMock, MagicMock
from lolibot.config import BotConfig
from lolibot.telegram.bot import get_context_command
from types import SimpleNamespace


@pytest.mark.asyncio
async def test_context_command_buttons(monkeypatch):
    # Simulate a config with multiple contexts
    config = BotConfig(
        bot_name="TestBot",
        default_timezone="UTC",
        context_name="test",
        openai_api_key="key",
        gemini_api_key="key",
        claude_api_key="key",
        telegram_bot_token="token",
        available_contexts=["default", "test", "work"],
        contexts={"default": {}, "test": {}, "work": {}},
        config_path=None,
    )
    # Patch get_switchable_contexts to exclude 'default'
    config.get_switchable_contexts = lambda: ["test", "work"]

    # Mock update and context
    update = MagicMock()
    update.message.text = "/context"
    update.message.reply_text = AsyncMock()
    context_ns = SimpleNamespace()
    context_ns.application = SimpleNamespace()
    context_ns.application.bot_data = {"config": config}

    await get_context_command(update, context_ns)
    # Should show buttons for 'test' and 'work', not 'default'
    args, kwargs = update.message.reply_text.call_args
    assert "default" not in args[0]
    assert "Available contexts: test, work" in args[0]
    assert "Current context:    test" in args[0]
