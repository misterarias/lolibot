"""Google API integration module for the Task Manager Bot."""

import logging
import os
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from lolibot.config import BotConfig
from lolibot.services import TaskData


# Google API scopes
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
]

logger = logging.getLogger(__name__)


def get_google_service(config: BotConfig, service_name: str):
    """Get authenticated Google API service."""
    creds = None
    creds_path = config.get_creds_path()
    token_file = creds_path / f"token_{service_name}.json"
    credentials_file = creds_path / "credentials.json"

    # Load existing token if available
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_info(json.load(open(token_file)), SCOPES)

    # Refresh token if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # Get new credentials if none exist
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    # Build and return the service
    return build(service_name, "v3" if service_name == "calendar" else "v1", credentials=creds)


def create_task(config: BotConfig, task_data: TaskData):
    """Create a task in Google Tasks."""
    try:
        service = get_google_service(config, "tasks")

        # Get task lists
        task_lists = service.tasklists().list().execute()

        # Use the first task list or create one if none exists
        if not task_lists.get("items"):
            task_list = service.tasklists().insert(body={"title": "TaskBot"}).execute()
            task_list_id = task_list["id"]
        else:
            task_list_id = task_lists["items"][0]["id"]

        # Create the task
        task = {
            "title": task_data.title,
            "notes": task_data.description,
            "due": f"{task_data.date}T23:59:59Z" if task_data.date else None,
        }
        logger.info(f"Creating task: {task}")

        result = service.tasks().insert(tasklist=task_list_id, body=task).execute()

        return result["id"]
    except Exception as e:
        logger.error(f"Error creating Google Task: {e}")
        return None


def create_calendar_event(config: BotConfig, event_data: TaskData):
    """Create an event in Google Calendar."""
    try:
        service = get_google_service(config, "calendar")

        # Set the start and end times
        start_time = event_data.time if event_data.time else "09:00"
        start_datetime = f"{event_data.date}T{start_time}:00"

        # Default event duration: 30 minutes
        end_datetime = datetime.fromisoformat(start_datetime)
        end_datetime = end_datetime + timedelta(minutes=30)
        end_datetime = end_datetime.isoformat()

        event = {
            "summary": event_data.title,
            "description": event_data.description,
            "start": {
                "dateTime": start_datetime,
                "timeZone": config.default_timezone,
            },
            "end": {
                "dateTime": end_datetime,
                "timeZone": config.default_timezone,
            },
            "reminders": {"useDefault": True},
        }
        # Add attendees if present
        if event_data.invitees:
            event["attendees"] = [{"email": email} for email in event_data.invitees]
        logger.info(f"Creating event: {event}")

        result = service.events().insert(calendarId="primary", body=event).execute()

        return result["id"]
    except Exception as e:
        logger.error(f"Error creating Google Calendar event: {e}")
        return None


def create_reminder(config: BotConfig, reminder_data: TaskData):
    """Create a reminder in Google Calendar."""
    try:
        service = get_google_service(config, "calendar")

        # Set the reminder time
        reminder_time = reminder_data.time if reminder_data.time else "09:00"
        reminder_datetime = f"{reminder_data.date}T{reminder_time}:00"

        # End time is 15 minutes after start for reminders
        end_datetime = datetime.fromisoformat(reminder_datetime)
        end_datetime = end_datetime + timedelta(minutes=15)
        end_datetime = end_datetime.isoformat()

        event = {
            "summary": f"REMINDER: {reminder_data.title}",
            "description": reminder_data.description,
            "start": {
                "dateTime": reminder_datetime,
                "timeZone": config.default_timezone,
            },
            "end": {
                "dateTime": end_datetime,
                "timeZone": config.default_timezone,
            },
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": 0}],
            },
        }
        logger.info(f"Creating reminder: {event}")

        result = service.events().insert(calendarId="primary", body=event).execute()

        return result["id"]
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        return None
