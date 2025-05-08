"""Telegram bot application module."""

import time
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

from lolibot.config import BotConfig
from lolibot.llm.processor import LLMProcessor
from lolibot.services.status import StatusItem, StatusType, status_service
from lolibot.task_manager import TaskManager

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! I'm your Task Manager Bot. Tell me about your tasks, "
        "events, or reminders, and I'll create them for you.\n\n"
        "Examples:\n"
        "- Create a task to review the project plan tomorrow\n"
        "- Schedule a meeting with Brian at 2pm on Friday\n"
        "- Remind me to follow up with marketing team next Monday at 10am"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "I can help you manage your tasks, events, and reminders. Just tell me "
        "what you need in natural language, and I'll extract the important details.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/status - Check if I'm connected to your Google account\n\n"
        "Examples of things you can say:\n"
        '- "Schedule a team meeting tomorrow at 3pm"\n'
        '- "Remind me to call John on Friday"\n'
        '- "Create a task to finish the report by next Tuesday"\n'
        '- "I need to send the invoice to finance department before Friday"'
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check the connection status to Google services."""
    config = context.application.bot_data.get("config")
    start_time = context.application.bot_data.get("start_time")
    uptime = time.time() - start_time
    uptime_str = f"{uptime // 3600:.0f}h {uptime % 3600 // 60:.0f}m {uptime % 60:.0f}s"

    status_list = status_service(config)
    status_list.append(StatusItem(f"Uptime: {uptime_str}", StatusType.INFO))

    info_messages = '\n'.join(
        f"{status_item.name}"
        for status_item in status_list
        if status_item.status_type == StatusType.INFO
    )

    ok_messages = '\n'.join(
        f"✅ {status_item.name}"
        for status_item in status_list
        if status_item.status_type == StatusType.OK
    )
    err_messages = '\n'.join(
        f"❌ {status_item.name}"
        for status_item in status_list
        if status_item.status_type == StatusType.ERROR
    )
    extra = ""
    if not err_messages:
        extra = 'All systems are operational 😊'
    elif not ok_messages:
        extra = 'All systems are DOWN ☹️'

    md_message = f"""
{info_messages}

{ok_messages}
{err_messages}

{extra}
"""

    await update.message.reply_markdown_v2(md_message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages."""
    user_message = update.message.text
    user_id = update.effective_user.id
    logger.debug(f"Received message from user {user_id}: {user_message}")

    # Inform the user that we're processing their message
    await update.message.reply_text("Processing your request...")

    # Extract task information using LLM
    task_data = LLMProcessor().process_text(user_message)

    # Process the task and get response
    response = TaskManager.process_task(user_id, user_message, task_data)

    # Send response
    await update.message.reply_text(response)


def run_telegram_bot(config: BotConfig):
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
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    logger.info("Starting Telegram bot")
    application.run_polling()
