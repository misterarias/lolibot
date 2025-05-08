"""Configuration module for the Task Manager Bot."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Google API scopes
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
]

# Telegram Bot settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# LLM API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Time zone setting
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "UTC")

# SQLite DB for persistence
DB_PATH = os.getenv("DB_PATH", "./taskbot.db")
