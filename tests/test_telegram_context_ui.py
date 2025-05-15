import pytest
from unittest.mock import AsyncMock, MagicMock
from lolibot.config import BotConfig
from lolibot.telegram.bot import context_command
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

    await context_command(update, context_ns)
    # Should show buttons for 'test' and 'work', not 'default'
    args, kwargs = update.message.reply_text.call_args
    assert "test" in args[0] and "work" in args[0]
    assert "default" not in args[0]
    assert "Available contexts: test, work" in args[0]
    assert "To change the context" in args[0]
    assert "Current context:    test" in args[0]
    # Should have reply_markup with two buttons
    assert kwargs["reply_markup"] is not None
    # Extract button texts for comparison
    button_texts = [[button.text for button in row] for row in kwargs["reply_markup"].keyboard]
    assert button_texts == [["test"], ["work"]]
