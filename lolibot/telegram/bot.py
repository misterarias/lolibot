"""Telegram bot application module."""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from ..config import TELEGRAM_BOT_TOKEN
from ..db import init_db
from ..bot import start, help_command, status, handle_message

logger = logging.getLogger(__name__)


def run_telegram_bot():
    """Start the Telegram bot."""
    # Initialize database
    init_db()

    # Check bot token
    if not TELEGRAM_BOT_TOKEN:
        logger.error("No Telegram bot token provided")
        return

    # Initialize the bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    logger.info("Starting Telegram bot")
    application.run_polling()
