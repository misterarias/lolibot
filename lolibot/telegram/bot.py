"""Telegram bot application module."""

import html
import json
import time
import logging
import traceback
from typing import List
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import BotCommand, Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from lolibot.config import BotConfig, change_context
from lolibot.db import save_task_to_db
from lolibot.services import StatusItem, StatusType
from lolibot.services.processor import TaskResponse, process_user_message
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


# noqa
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


def format_status_commabd(status_list: List[StatusItem]) -> str:
    info_messages = "\n".join(f"ℹ️ {status_item.name}" for status_item in status_list if status_item.status_type == StatusType.INFO)
    ok_messages = "\n".join(f"✅ {status_item.name}" for status_item in status_list if status_item.status_type == StatusType.OK)
    err_messages = "\n".join(f"❌ {status_item.name}" for status_item in status_list if status_item.status_type == StatusType.ERROR)
    extra = ""
    if not err_messages:
        extra = "All systems are operational 😊"
    elif not ok_messages:
        extra = "All systems are DOWN ☹️"

    return f"""
{info_messages}
{ok_messages}
{err_messages}

{extra}
"""


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check the connection status to Google services."""
    config = context.application.bot_data.get("config")
    start_time = context.application.bot_data.get("start_time")
    uptime = time.time() - start_time
    uptime_str = f"{uptime // 3600:.0f}h {uptime % 3600 // 60:.0f}m {uptime % 60:.0f}s"

    status_list = status_service(config)
    status_list.append(StatusItem(f"Uptime: {uptime_str}", StatusType.INFO))

    response = format_status_commabd(status_list)
    await update.message.reply_markdown_v2(response)


def escapeHtmlResponse(response: str) -> str:
    # Escapes Telegram MarkdownV2 special characters
    # See: https://core.telegram.org/bots/api#markdownv2-style
    for c in set(["_", "*", "[", "]", "(", ")", "~", "`", "#", "+", "-", "=", "|", "{", "}", ".", "!", "<", ">"]):
        response = response.replace(c, f"\\{c}")
    return response


def format_task_response(task_response: TaskResponse) -> str:
    if not task_response.processed:
        response = "Error processing message 👎"
    else:
        time_date_str = (
            f"- *{task_response.task.date}@{task_response.task.time}*" if task_response.task.date and task_response.task.time else ""
        )
        response = f"""\
{task_response.task.task_type.capitalize()} created 👍

{escapeHtmlResponse(task_response.task.title)} {time_date_str}

> {escapeHtmlResponse(task_response.task.description)}
"""
        if task_response.task.invitees:
            response += f"Invitees: {', '.join(task_response.task.invitees)}\n\n"

    logger.info(f"Formatted response: {response}")
    return response


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages."""
    user_message = update.message.text
    user_id = update.effective_user.id
    logger.debug(f"Received message from user {user_id}: {user_message}")

    # Inform the user that we're processing their message
    # await update.message.reply_text("Procesando...")

    config = context.application.bot_data.get("config")

    task_response = process_user_message(config, user_message)

    # Store info in the database
    save_task_to_db(user_id, user_message, task_response.task, task_response.processed)

    # render a nice response using HTML
    response = format_task_response(task_response)

    # The response may include extra info about invitees (just me mode)
    await update.message.reply_markdown_v2(response)


def format_get_context(config: BotConfig) -> str:
    return f"""
    Current context:    *{config.context_name}*

    Available contexts: {', '.join(config.get_switchable_contexts())}
"""


async def get_context_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change the context for the bot."""
    config: BotConfig = context.application.bot_data.get("config")

    response = format_get_context(config)
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


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    config: BotConfig = context.application.bot_data.get("config")
    if not config.telegram_feedback_chat_id:
        logger.error("No Telegram dev chat id for feedback. Exiting handler")
        return

    await context.bot.send_message(chat_id=config.telegram_feedback_chat_id, text=message, parse_mode=ParseMode.HTML)


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
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("contexts", get_context_command))

    # error handler
    application.add_error_handler(error_handler)

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
