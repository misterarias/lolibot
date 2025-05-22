"""Telegram bot application module."""

import time
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import BotCommand

from lolibot.config import BotConfig
from lolibot.telegram import (
    error_handler,
    get_context_command,
    help_command,
    message_handler,
    set_context_command,
    start_command,
    status_command,
)


logger = logging.getLogger(__name__)


def run_telegram_bot(config: BotConfig):  # noqa
    """Start the Telegram bot."""
    # Check bot token
    if not config.telegram_bot_token:
        logger.error("No Telegram bot token provided")
        return

    # Initialize the bot and set config as bot data
    application = Application.builder().token(config.telegram_bot_token).build()
    application.bot_data["config"] = config
    application.bot_data["start_time"] = time.time()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command.command))
    application.add_handler(CommandHandler("help", help_command.command))
    application.add_handler(CommandHandler("status", status_command.command))
    application.add_handler(CommandHandler("contexts", get_context_command.command))

    # error handler
    application.add_error_handler(error_handler.error_handler)

    for ctx_name in config.get_switchable_contexts():
        application.add_handler(CommandHandler(f"set_{ctx_name}", set_context_command.command))

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler.handler))

    switchable_contexts = config.get_switchable_contexts()
    menu_commands = [
        BotCommand("status", "Show status of APIs and services"),
        BotCommand("contexts", "Check or change the context for the bot configuration"),
    ]
    for ctx_name in switchable_contexts:
        menu_commands.append(BotCommand(f"set_{ctx_name}", f"Switch to context '{ctx_name}'"))

    # Schedule the menu setup as a startup task
    application.post_init = lambda x: application.bot.set_my_commands(menu_commands)

    # Start the Bot
    logger.info("Starting Telegram bot")
    application.run_polling()
