#!/usr/bin/env python3
"""
Task Manager - Main Application
An application that processes natural language to create tasks, calendar events, and reminders.
Available interfaces:
- Command line
- Telegram bot
"""
from pathlib import Path
import click
import logging
from lolibot.cli.commands import (
    apunta_command,
    change_context_command,
    status_command,
    telegram_command,
)
from lolibot.db import init_db


def configure_logging(verbosity: int):
    """Configure logging based on verbosity level."""
    # Reset root logger
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Map verbosity to logging levels:
    # 0 -> WARNING (30)
    # 1 -> INFO (20)
    # 2 -> DEBUG (10)
    # 3 -> NOTSET (0)
    level = max(logging.NOTSET, logging.WARNING - (verbosity * 10))
    logging.basicConfig(
        format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s", level=level, force=True  # Force reconfiguration of the root logger
    )

    # Suppress some library logs unless we're at maximum verbosity
    if level > logging.NOTSET:
        for lib in [
            "googleapiclient",
            "google_auth_httplib2",
            "google_auth_oauthlib",
            "httpx",
            "httpcore",
            "telegram.ext",
        ]:
            logging.getLogger(lib).setLevel(logging.WARNING)


@click.group()
@click.option("-v", "--verbose", count=True, help="Increase verbosity (up to -vvv)")
@click.option(
    "--config-path",
    default=str(Path("config.toml")),
    type=click.Path(exists=True, path_type=Path),
    help="Path to the TOML configuration file",
)
@click.pass_context
def main(ctx, verbose, config_path):
    """Task Manager - Create tasks, events, and reminders using natural language."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path

    configure_logging(verbose)
    init_db()

    # Load the configuration
    from lolibot.config import BotConfig

    ctx.obj["config"] = BotConfig.from_file(config_path)


# Add the CLI commands directly
main.add_command(apunta_command)
main.add_command(telegram_command)
main.add_command(status_command)
main.add_command(change_context_command)


if __name__ == "__main__":
    main()
