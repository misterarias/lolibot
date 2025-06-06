"""CLI commands for the task manager."""

import logging
import click

from lolibot import UserMessage
from lolibot.config import BotConfig
from lolibot.services import TaskResponse, processor
from lolibot.services.status import StatusType, status_service
from lolibot.telegram.bot import run_telegram_bot

logger = logging.getLogger(__name__)


def click_secho_task_response(task_response: TaskResponse):
    # render a nice response using click
    if not task_response.processed:
        click.secho("Error processing message 👎", fg="red")
        return

    click.secho(f"{task_response.task.task_type.capitalize()} created 👍", fg="green")

    time_date_str = f"- {task_response.task.date}@{task_response.task.time}" if task_response.task.date and task_response.task.time else ""
    response = f"""
{task_response.task.title} {time_date_str}

{task_response.task.description}
"""
    if task_response.task.invitees:
        response += f"Invitees: {', '.join(task_response.task.invitees)}\n\n"
    click.echo(response)


@click.command(name="apunta")
@click.argument("text", nargs=-1)
@click.pass_context
def apunta_command(ctx, text):
    """Create a task, event, or reminder using natural language.

    TEXT is your natural language description of what you want to create.
    For example: "Schedule a meeting with John tomorrow at 2pm"
    """
    config = ctx.obj["config"]

    # Process the text using LLM
    text = " ".join(text)

    user_message = UserMessage(message=text, user_id="cli_user")
    logger.debug(f"Processing {user_message}...")
    task_responses = processor.process_user_message(config, user_message)

    # Format and print the response
    for task_response in task_responses:
        click_secho_task_response(task_response)


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
        elif status_item.status_type == StatusType.WARNING:
            click.secho(f"⚠️ {status_item.name}", fg="yellow")
        elif status_item.status_type == StatusType.INFO:
            click.secho(f"{status_item.name}", fg="blue")
        else:
            click.secho(f"{status_item.name} (unknown status)", fg="magenta")


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
        config.change_context(context_name)
        click.secho(f"Context changed to '{context_name}'", fg="green")
    except ValueError as e:
        click.secho(f"Error: {e}", fg="red")
        return 1
