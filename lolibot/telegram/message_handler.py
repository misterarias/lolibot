import logging
from typing import List
from lolibot import UserMessage
from lolibot.services.processor import TaskResponse, process_user_message
from telegram import Update
from telegram.ext import ContextTypes
from .utils import escapeMarkdownCharacters

logger = logging.getLogger(__name__)


def format_command(task_responses: List[TaskResponse]) -> List[str]:
    """Format a task response into a Markdown message for Telegram."""
    # Start with a summary
    total = len(task_responses)  # Total attempted tasks
    success = sum(1 for p in task_responses if p.processed)  # Count successful tasks
    if success == 0:
        return ["No tasks were created 👎\n"]

    responses = [f"Processed {success}/{total} tasks 👍"]

    # Add details for successful tasks
    for task_response in task_responses:
        if not task_response.processed:
            continue

        task = task_response.task
        time_date_str = ""
        if task.task_type == "event":
            time_date_str = f"{escapeMarkdownCharacters(' - ')} *{task.date}@{task.time}*"

        responses.append(f"\n✅ {escapeMarkdownCharacters(task.title)}{time_date_str}")

    # Add details for failed tasks
    for task_response in task_responses:
        if task_response.processed or not task_response.feedback:
            continue
        responses.append(f"\n>❌ {escapeMarkdownCharacters(task_response.feedback)}")

    return responses


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages."""
    message = update.message.text
    user_id = update.effective_user.id
    user_message = UserMessage(message=message, user_id=user_id)
    logger.debug(f"Received {user_message}...")

    # Inform the user that we're processing their message
    # await update.message.reply_text("Procesando...")

    config = context.application.bot_data.get("config")

    task_responses = process_user_message(config, user_message)

    # render a nice response using HTML
    responses = format_command(task_responses)

    # try to send the response as HTML first
    for response in responses:
        try:
            await update.message.reply_markdown_v2(response)
        except Exception as e:
            logger.warning(f"Failed to send message as HTML: {response}: {e}")
            # fallback to plain text
            await update.message.reply_text(response)
