from telegram import Update
from telegram.ext import ContextTypes

from lolibot.config import BotConfig


def format_command(config: BotConfig) -> str:
    return f"""
    Current context:    *{config.current_context}*

    Available contexts: {', '.join(config.available_contexts)}
"""


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change the context for the bot."""
    config: BotConfig = context.application.bot_data.get("config")

    response = format_command(config)
    await update.message.reply_markdown_v2(response, reply_markup=None)
