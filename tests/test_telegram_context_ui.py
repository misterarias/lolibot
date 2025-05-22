from unittest.mock import AsyncMock
import pytest

from lolibot.telegram.get_context_command import command as get_context_command
from types import SimpleNamespace


@pytest.mark.asyncio
async def test_get_context_command(multi_contexts_config):
    # Mock update and context
    mock_update = AsyncMock()
    mock_update.message.text = "/context"
    mock_update.message.reply_text = AsyncMock()

    context_ns = SimpleNamespace()
    context_ns.application = SimpleNamespace()
    context_ns.application.bot_data = {"config": multi_contexts_config}

    await get_context_command(mock_update, context_ns)

    args, _ = mock_update.message.reply_markdown_v2.call_args
    assert "default" not in args[0]
    assert "Available contexts: test, personal" in args[0]
    assert "Current context:    *test*" in args[0]
