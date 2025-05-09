"""CLI commands for the task manager."""

import logging
import click

from lolibot.services.status import StatusType, status_service
from lolibot.telegram.bot import run_telegram_bot
from ..llm.processor import LLMProcessor
from ..services.task_manager import TaskData, TaskManager

logger = logging.getLogger(__name__)


@click.command()
@click.argument("text", nargs=-1)
@click.pass_context
def apunta(ctx, text):
    """Create a task, event, or reminder using natural language.

    TEXT is your natural language description of what you want to create.
    For example: "Schedule a meeting with John tomorrow at 2pm"
    """
    config = ctx.obj["config"]
    task_manager = TaskManager(config)

    # Process the text using LLM
    text = " ".join(text)
    logger.debug(f"Processing text: {text}")

    task_data = LLMProcessor(config).process_text(text)

    # Create the task (using a dummy user_id for CLI)
    response = task_manager.process_task("cli_user", text, TaskData.from_dict(task_data))
    click.echo(response)


@click.command()
@click.pass_context
def status(ctx):
    """Check connection status to various services."""
    config = ctx.obj["config"]
    status_list = status_service(config)
    for status_item in status_list:
        if status_item.status_type == StatusType.OK:
            click.secho(f"✓ {status_item.name}", fg="green")
        elif status_item.status_type == StatusType.ERROR:
            click.secho(f"✗ {status_item.name}", fg="red")
        else:
            click.secho(f"{status_item.name}", fg="yellow")


@click.command()
@click.pass_context
def telegram(ctx):
    """Start the Telegram bot."""
    config = ctx.obj["config"]
    run_telegram_bot(config=config)
