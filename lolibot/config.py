"""Configuration module for the Task Manager Bot."""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
log_level = logging.DEBUG if debug_mode else logging.INFO
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=log_level,
)

# supress some  library logs
for lib in ["googleapiclient", "google_auth_httplib2", "google_auth_oauthlib", "httpx", "httpcore", "telegram.ext"]:
    logging.getLogger(lib).setLevel(logging.WARNING)


# Google API scopes
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
]

# Telegram Bot settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# LLM API settings
OPENAPI_API_KEY = os.getenv("OPENAPI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Time zone setting
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "UTC")

# SQLite DB for persistence
DB_PATH = os.getenv("DB_PATH", "./taskbot.db")
