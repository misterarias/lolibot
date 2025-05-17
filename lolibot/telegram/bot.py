"""Telegram bot application module."""

import time
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import BotCommand, Update
from telegram.ext import ContextTypes

from lolibot.config import BotConfig, change_context
from lolibot.db import save_task_to_db
from lolibot.services import StatusItem, StatusType, processor
from lolibot.services.status import status_service


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
        "/status - Check status of APIs and services\n\n"
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

    info_messages = "\n".join(f"ℹ️ {status_item.name}" for status_item in status_list if status_item.status_type == StatusType.INFO)
    ok_messages = "\n".join(f"✅ {status_item.name}" for status_item in status_list if status_item.status_type == StatusType.OK)
    err_messages = "\n".join(f"❌ {status_item.name}" for status_item in status_list if status_item.status_type == StatusType.ERROR)
    extra = ""
    if not err_messages:
        extra = "All systems are operational 😊"
    elif not ok_messages:
        extra = "All systems are DOWN ☹️"

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

    config = context.application.bot_data.get("config")

    task_response = processor.process_user_message(config, user_message)

    # Store info in the database
    save_task_to_db(user_id, user_message, task_response.task, task_response.processed)

    # render a nice response using HTML
    if not task_response.processed:
        response = "Error processing message 👎"
    else:
        time_date_str = (
            f"- *{task_response.task.date}@{task_response.task.time}*" if task_response.task.date and task_response.task.time else ""
        )
        response = f"""\
{task_response.task.task_type.capitalize()} created 👍

{task_response.task.title} {time_date_str}

> {task_response.task.description}
"""
        if task_response.task.invitees:
            response += f"Invitees: {', '.join(task_response.task.invitees)}\n\n"

    # The response may include extra info about invitees (just me mode)
    await update.message.reply_markdown_v2(response)


async def get_context_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change the context for the bot."""
    config: BotConfig = context.application.bot_data.get("config")

    switchable_contexts = config.get_switchable_contexts()

    response = f"""
Current context:    *{config.context_name}*

Available contexts: {', '.join(switchable_contexts)}
"""
    await update.message.reply_markdown_v2(response, reply_markup=None)


async def set_context_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change the context for the bot."""
    config: BotConfig = context.application.bot_data.get("config")
    context_name = update.message.text.split("_")[1].strip()
    try:
        new_config = change_context(context_name, config)
        context.application.bot_data["config"] = new_config
        await update.message.reply_text(f"✅ Context changed to {context_name}")
    except Exception as e:
        logger.error(f"Error changing context: {e}")
        await update.message.reply_text(f"❌ Error changing context: {e}")


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
    application.add_handler(CommandHandler("contexts", get_context_command))

    for ctx_name in config.get_switchable_contexts():
        application.add_handler(CommandHandler(f"set_{ctx_name}", set_context_command))

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

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
