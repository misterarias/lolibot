import logging
from typing import List
from lolibot.db import save_task_to_db
from lolibot.services.processor import TaskResponse, process_user_message
from telegram import Update
from telegram.ext import ContextTypes
from .utils import escapeMarkdownCharacters

logger = logging.getLogger(__name__)


def format_command(task_responses: List[TaskResponse]) -> str:
    """Format a task response into a Markdown message for Telegram."""
    # Start with a summary
    total = len(task_responses)  # Total attempted tasks
    success = sum(1 for p in task_responses if p.processed)  # Count successful tasks
    response = [f"Processed {success}/{total} tasks 👍" if success else "No tasks were created 👎\n"]

    # Add each task's feedback message
    # response.extend(f"\n{escapeMarkdownCharacters(r.feedback)}" for r in task_responses)

    # Add details for successful tasks
    for task_response in task_responses:
        if not task_response.processed:
            continue

        task = task_response.task
        time_date_str = ""
        if task.task_type == "event":
            time_date_str = f"{escapeMarkdownCharacters(' - ')} *{task.date}@{task.time}*"

        response.extend(
            [
                f"\n{escapeMarkdownCharacters('─' * 20)}",
                f"\n{escapeMarkdownCharacters(task.title)}{time_date_str}",
            ]
        )
        if len(task.description) > 20:
            response.append(f"\n> {escapeMarkdownCharacters(task.description)}")

        if task.invitees:
            response.append(f"\nInvitees: {escapeMarkdownCharacters(', '.join(task.invitees))}")

    # Add details for failed tasks
    for task_response in task_responses:
        if task_response.processed or not task_response.feedback:
            continue
        response.append(f"\n> {escapeMarkdownCharacters(task_response.feedback)}")

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

    task_responses = process_user_message(config, user_message)

    # Store info in the database for each task
    for response in task_responses:
        save_task_to_db(user_id, user_message, response.task, response.processed)

    # render a nice response using HTML
    response = format_command(task_responses)

    # try to send the response as HTML first
    try:
        await update.message.reply_markdown_v2(response)
    except Exception:
        logger.warning(f"Failed to send message as HTML: {response}")
        # fallback to plain text
        await update.message.reply_text(response)
