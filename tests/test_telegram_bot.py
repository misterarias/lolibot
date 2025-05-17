from unittest.mock import AsyncMock, patch

import pytest
from lolibot.telegram.bot import start_command


@patch("lolibot.telegram.bot.Update")
@patch("lolibot.telegram.bot.ContextTypes.DEFAULT_TYPE")
@pytest.mark.asyncio
async def test_start_command(mock_context, mock_update):
    mock_update.message.reply_text = AsyncMock()

    await start_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(
        "Hi! I'm your Task Manager Bot. Tell me about your tasks, "
        "events, or reminders, and I'll create them for you.\n\n"
        "Examples:\n- Create a task to review the project plan tomorrow\n- Schedule a meeting with Brian at 2pm on Friday\n"
        "- Remind me to follow up with marketing team next Monday at 10am"
    )
