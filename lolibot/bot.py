"""Telegram bot handlers module."""
from telegram import Update
from telegram.ext import ContextTypes
from lolibot.config import logger, LLM_API_KEY, LLM_PROVIDER
from lolibot.llm import LLMProcessor
from lolibot.task_manager import TaskManager
from lolibot.google_api import get_google_service


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! I'm your Task Manager Bot. Tell me about your tasks, "
        "events, or reminders, and I'll create them for you.\n\n"
        "Examples:\n"
        "- Create a task to review the project plan tomorrow\n"
        "- Schedule a meeting with Brian at 2pm on Friday\n"
        "- Remind me to follow up with marketing team next Monday at 10am"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "I can help you manage your tasks, events, and reminders. Just tell me "
        "what you need in natural language, and I'll extract the important details.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/status - Check if I'm connected to your Google account\n\n"
        "Examples of things you can say:\n"
        '- "Schedule a team meeting tomorrow at 3pm"\n'
        '- "Remind me to call John on Friday"\n'
        '- "Create a task to finish the report by next Tuesday"\n'
        '- "I need to send the invoice to finance department before Friday"'
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check the connection status to Google services."""
    message = []

    # Check Calendar connection
    try:
        calendar = get_google_service("calendar")
        calendar.events().list(calendarId="primary", maxResults=1).execute()
        message.append("✅ Connected to Google Calendar")
    except Exception as e:
        message.append(f"❌ Not connected to Google Calendar: {str(e)}")

    # Check Tasks connection
    try:
        tasks = get_google_service("tasks")
        tasks.tasklists().list(maxResults=1).execute()
        message.append("✅ Connected to Google Tasks")
    except Exception as e:
        message.append(f"❌ Not connected to Google Tasks: {str(e)}")

    # Check LLM API connection
    if LLM_API_KEY:
        message.append(f"✅ LLM Provider configured: {LLM_PROVIDER}")
    else:
        message.append("⚠️ No LLM API configured, using fallback regex parser")

    await update.message.reply_text("\n".join(message))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages."""
    user_message = update.message.text
    user_id = update.effective_user.id

    # Inform the user that we're processing their message
    await update.message.reply_text("Processing your request...")

    # Extract task information using LLM
    task_data = LLMProcessor.process_text(user_message)

    # Process the task and get response
    response = TaskManager.process_task(user_id, user_message, task_data)

    # Send response
    await update.message.reply_text(response)
