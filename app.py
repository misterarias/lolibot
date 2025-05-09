#!/usr/bin/env python3
"""
Task Manager - Main Application
An application that processes natural language to create tasks, calendar events, and reminders.
Available interfaces:
- Command line
- Telegram bot
"""
import os
from pathlib import Path
import click
import logging
from lolibot.cli.commands import create, status, telegram
from lolibot.db import init_db


def configure_logging(verbosity: int):
    """Configure logging based on verbosity level."""
    levels = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG, 3: logging.NOTSET}  # default  # -v  # -vv  # -vvv (maximum verbosity)
    level = levels.get(min(verbosity, max(levels.keys())), logging.WARNING)

    # Set the DEBUG_MODE environment variable for other modules
    os.environ["DEBUG_MODE"] = "true" if level <= logging.DEBUG else "false"

    # Configure the root logger
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=level,
    )

    # Suppress some library logs unless we're at maximum verbosity
    if level > logging.NOTSET:
        for lib in ["googleapiclient", "google_auth_httplib2", "google_auth_oauthlib", "httpx", "httpcore", "telegram.ext"]:
            logging.getLogger(lib).setLevel(logging.WARNING)


@click.group()
@click.option("-v", "--verbose", count=True, help="Increase verbosity (up to -vvv)")
@click.option("--config-path", default=Path("config.toml"), type=click.Path(exists=True), help="Path to the TOML configuration file")
@click.pass_context
def main(ctx, verbose, config_path):
    """Task Manager - Create tasks, events, and reminders using natural language."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path

    configure_logging(verbose)
    init_db()

    # Load the configuration
    from lolibot.config import load_config

    ctx.obj["config"] = load_config(config_path)


# Add the CLI commands directly
main.add_command(create)
main.add_command(telegram)
main.add_command(status)


if __name__ == "__main__":
    main()
