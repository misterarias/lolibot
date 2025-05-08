"""CLI commands for the task manager."""

import click
from ..llm.processor import LLMProcessor
from ..task_manager import TaskManager


@click.group()
def cli():
    """Task Manager CLI - Create tasks, events, and reminders using natural language."""
    pass


@cli.command()
@click.argument("text")
def create(text):
    """Create a task, event, or reminder using natural language.
    
    TEXT is your natural language description of what you want to create.
    For example: "Schedule a meeting with John tomorrow at 2pm"
    """
    # Process the text using LLM
    task_data = LLMProcessor().process_text(text)
    
    # Create the task (using a dummy user_id for CLI)
    response = TaskManager.process_task("cli_user", text, task_data)
    click.echo(response)


@cli.command()
def status():
    """Check connection status to various services."""
    from ..llm.processor import LLMProcessor
    
    # Check LLM providers
    llm_processor = LLMProcessor()
    for provider in llm_processor.PROVIDERS:
        if provider.check_connection():
            click.secho(f"✓ Connected to {provider.name()} API", fg="green")
        else:
            click.secho(f"✗ Not connected to {provider.name()} API", fg="red")

    # Check Google services
    from ..google_api import get_google_service
    try:
        calendar = get_google_service("calendar")
        calendar.events().list(calendarId="primary", maxResults=1).execute()
        click.secho("✓ Connected to Google Calendar", fg="green")
    except Exception as e:
        click.secho(f"✗ Not connected to Google Calendar: {str(e)}", fg="red")

    try:
        tasks = get_google_service("tasks")
        tasks.tasklists().list(maxResults=1).execute()
        click.secho("✓ Connected to Google Tasks", fg="green")
    except Exception as e:
        click.secho(f"✗ Not connected to Google Tasks: {str(e)}", fg="red")
