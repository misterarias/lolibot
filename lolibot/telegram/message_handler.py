import logging
from lolibot.db import save_task_to_db
from lolibot.services.processor import TaskResponse, process_user_message
from telegram import Update
from telegram.ext import ContextTypes
from .utils import escapeMarkdownCharacters

logger = logging.getLogger(__name__)


def format_command(task_response: TaskResponse) -> str:
    """Format a task response into a Markdown message for Telegram."""
    # Start with a summary
    total = len(task_response.messages)  # Total attempted tasks
    success = sum(1 for p in task_response.processed if p)
    response = [f"Processed {success} of {total} tasks 👍" if success else "No tasks were created 👎"]

    # Add each task's feedback message
    response.extend(f"\n{escapeMarkdownCharacters(msg)}" for msg in task_response.messages)

    # Add details for successful tasks
    for i, (task, was_processed) in enumerate(zip(task_response.tasks, task_response.processed)):
        if not was_processed:
            continue

        time_date_str = ""
        if task.date and task.time:
            time_date_str = f"{escapeMarkdownCharacters(' - ')} *{task.date}@{task.time}*"

        response.extend(
            [
                f"\n{escapeMarkdownCharacters('─' * 30)}",
                f"\n{task.task_type.capitalize()}:",
                f"\n{escapeMarkdownCharacters(task.title)}{time_date_str}",
                f"\n> {escapeMarkdownCharacters(task.description)}",
            ]
        )

        if task.invitees:
            response.append(f"\nInvitees: {escapeMarkdownCharacters(', '.join(task.invitees))}")

    result = "".join(response)
    logger.info(f"Formatted response: {result}")
    return result


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages."""
    user_message = update.message.text
    user_id = update.effective_user.id
    logger.debug(f"Received message from user {user_id}: {user_message}")

    # Inform the user that we're processing their message
    # await update.message.reply_text("Procesando...")

    config = context.application.bot_data.get("config")

    task_response = process_user_message(config, user_message)

    # Store info in the database for each task
    for task, was_processed in zip(task_response.tasks, task_response.processed):
        save_task_to_db(user_id, user_message, task, was_processed)

    # render a nice response using HTML
    response = format_command(task_response)

    # try to send the response as HTML first
    try:
        await update.message.reply_markdown_v2(response)
    except Exception:
        logger.warning(f"Failed to send message as HTML: {response}")
        # fallback to plain text
        await update.message.reply_text(response)
