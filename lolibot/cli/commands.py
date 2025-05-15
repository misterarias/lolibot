"""CLI commands for the task manager."""

import logging
import click

from lolibot.config import BotConfig, change_context
from lolibot.services.middleware.not_task import NotTaskMiddleWare
from lolibot.services.status import StatusType, status_service
from lolibot.telegram.bot import run_telegram_bot
from lolibot.services.middleware import (
    MiddlewarePipeline,
    JustMeInviteeMiddleware,
    DateValidationMiddleware,
    TitlePrefixTruncateMiddleware,
)
from ..llm.processor import LLMProcessor
from ..services.task_manager import TaskData, TaskManager

logger = logging.getLogger(__name__)


@click.command(name="apunta")
@click.argument("text", nargs=-1)
@click.pass_context
def apunta_command(ctx, text):
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

    pipeline = MiddlewarePipeline(
        [
            DateValidationMiddleware(),
            TitlePrefixTruncateMiddleware(config.bot_name),
            JustMeInviteeMiddleware(getattr(config, "default_invitees", [])),
            NotTaskMiddleWare(),
        ]
    )
    processed_data = pipeline.process(text, TaskData.from_dict(task_data))

    # Create the task (using a dummy user_id for CLI)
    response = task_manager.process_task("cli_user", text, processed_data)
    # The response may include extra info about invitees (just me mode)
    click.echo(response)


@click.command(name="status")
@click.pass_context
def status_command(ctx):
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


@click.command(name="telegram")
@click.pass_context
def telegram_command(ctx):
    """Start the Telegram bot."""
    config = ctx.obj["config"]
    run_telegram_bot(config=config)


@click.command("set-context")
@click.argument("context_name")
@click.pass_context
def change_context_command(ctx, context_name: str):
    """Change the current context of the bot and persist it."""
    config: BotConfig = ctx.obj["config"]
    try:
        change_context(context_name, config)
        click.secho(f"Context changed to '{context_name}'", fg="green")
    except ValueError as e:
        click.secho(f"Error: {e}", fg="red")
        return 1
