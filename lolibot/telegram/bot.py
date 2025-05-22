"""Telegram bot application module."""

import sys
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


def create_application(config: BotConfig) -> Application:
    application = Application.builder().token(config.telegram_token).build()
    application.bot_data["config"] = config

    return application


def run_telegram_bot(config: BotConfig):  # noqa
    """Start the Telegram bot."""
    # Check bot token
    if not config.telegram_token:
        logger.error("No Telegram bot token provided in config.")
        sys.exit(1)

    application = create_application(config)
    application.bot_data["start_time"] = time.time()

    application.add_handler(CommandHandler("start", start_command.command))
    application.add_handler(CommandHandler("help", help_command.command))
    application.add_handler(CommandHandler("status", status_command.command))
    application.add_handler(CommandHandler("contexts", get_context_command.command))

    application.add_error_handler(error_handler.handler)

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler.handler))

    menu_commands = [
        BotCommand("status", "Show status of APIs and services"),
        BotCommand("contexts", "Check or change the context for the bot configuration"),
    ]

    for ctx_name in config.available_contexts:
        application.add_handler(CommandHandler(f"set_{ctx_name}", set_context_command.command))
        menu_commands.append(BotCommand(f"set_{ctx_name}", f"Switch to context '{ctx_name}'"))

    # Schedule the menu setup as a startup task
    application.post_init = lambda x: application.bot.set_my_commands(menu_commands)

    # Start the Bot
    logger.info("Starting Telegram bot")
    application.run_polling()
