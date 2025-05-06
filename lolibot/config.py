"""Configuration module for the Task Manager Bot."""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Google API scopes
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
]

# Telegram Bot settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# LLM API settings
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic, or gemini

# Time zone setting
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "UTC")

# SQLite DB for persistence
DB_PATH = os.getenv("DB_PATH", "./taskbot.db")
