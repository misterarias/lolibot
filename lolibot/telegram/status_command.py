import time
from typing import List
from telegram import Update
from telegram.ext import ContextTypes

from lolibot.services import StatusItem, StatusType
from lolibot.services.status import status_service
from lolibot.telegram.utils import escapeMarkdownCharacters


def format_command(status_list: List[StatusItem]) -> str:
    info_messages = "\n".join(
        f"ℹ️ {escapeMarkdownCharacters(status_item.name)}" for status_item in status_list if status_item.status_type == StatusType.INFO
    )
    ok_messages = "\n".join(
        f"✅ {escapeMarkdownCharacters(status_item.name)}" for status_item in status_list if status_item.status_type == StatusType.OK
    )
    warning_messages = "\n".join(
        f"⚠️ {escapeMarkdownCharacters(status_item.name)}" for status_item in status_list if status_item.status_type == StatusType.WARNING
    )
    err_messages = "\n".join(
        f"❌ {escapeMarkdownCharacters(status_item.name)}" for status_item in status_list if status_item.status_type == StatusType.ERROR
    )

    return f"""
{info_messages}
{ok_messages}
{warning_messages}
{err_messages}
"""


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check the connection status to Google services."""
    config = context.application.bot_data.get("config")
    start_time = context.application.bot_data.get("start_time")
    uptime = time.time() - start_time
    uptime_str = f"{uptime // 3600:.0f}h {uptime % 3600 // 60:.0f}m {uptime % 60:.0f}s"

    status_list = status_service(config)
    status_list.append(StatusItem(f"Uptime: {uptime_str}", StatusType.INFO))

    response = format_command(status_list)
    await update.message.reply_markdown_v2(response)
