#!/usr/bin/env python3
"""
Task Manager - Main Application
An application that processes natural language to create tasks, calendar events, and reminders.
Available interfaces:
- Telegram bot
- Command-line interface
"""
import click
from lolibot.cli import cli
from lolibot.telegram import run_telegram_bot


@click.group()
def main():
    """Task Manager - Create tasks, events, and reminders using natural language."""
    pass


# Add the CLI commands as a subgroup
main.add_command(cli, name="cli")


@main.command()
def bot():
    """Start the Telegram bot."""
    run_telegram_bot()


if __name__ == "__main__":
    main()
