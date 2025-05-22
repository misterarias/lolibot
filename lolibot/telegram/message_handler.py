import logging
from lolibot.db import save_task_to_db
from lolibot.services.processor import TaskResponse, process_user_message
from telegram import Update
from telegram.ext import ContextTypes
from .utils import escapeMarkdownCharacters

logger = logging.getLogger(__name__)


def format_command(task_response: TaskResponse) -> str:
    if not task_response.processed:
        return "Error processing message 👎"

    time_date_str = f"{task_response.task.date}@{task_response.task.time}" if task_response.task.date and task_response.task.time else ""
    if time_date_str != "":
        time_date_str = f"{escapeMarkdownCharacters(' - ')} *{time_date_str}*"

    response = f"""\
{task_response.task.task_type.capitalize()} created 👍

{escapeMarkdownCharacters(task_response.task.title)}{time_date_str}

> {escapeMarkdownCharacters(task_response.task.description)}
"""
    if task_response.task.invitees:
        response += f"Invitees: {', '.join(task_response.task.invitees)}\n\n"

    logger.info(f"Formatted response: {response}")
    return response


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    response = format_command(task_response)

    # try to send the response as HTML first
    try:
        await update.message.reply_markdown_v2(response)
    except Exception:
        logger.warning(f"Failed to send message as HTML: {response}")
        # fallback to plain text
        await update.message.reply_text(response)
