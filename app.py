#!/usr/bin/env python3
"""
Task Manager Bot - Main Application
A bot that processes natural language to create tasks, calendar events, and reminders.
"""
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)
from lolibot.config import logger, TELEGRAM_BOT_TOKEN
from lolibot.db import init_db
from lolibot.bot import start, help_command, status, handle_message


def main():
    """Start the bot."""
    # Initialize database
    init_db()

    # Initialize the Telegram bot
    if not TELEGRAM_BOT_TOKEN:
        logger.error("No Telegram bot token provided")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()


if __name__ == "__main__":
    main()
