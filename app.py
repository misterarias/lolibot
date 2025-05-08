#!/usr/bin/env python3
"""
Task Manager - Main Application
An application that processes natural language to create tasks, calendar events, and reminders.
Available interfaces:
- Telegram bot
- Command-line interface
"""
import click
from lolibot.cli.commands import create, status, telegram


@click.group()
def main():
    """Task Manager - Create tasks, events, and reminders using natural language."""
    pass


# Add the CLI commands directly
main.add_command(create)
main.add_command(status)
main.add_command(telegram)


if __name__ == "__main__":
    main()
