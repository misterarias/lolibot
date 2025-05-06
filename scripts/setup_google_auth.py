#!/usr/bin/env python3
"""
Google API Authentication Setup Script
This script helps with setting up authentication for Google Calendar and Tasks.
"""
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Google API scopes
SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/tasks"]


def setup_auth():
    """Set up authentication with Google APIs."""
    print("Setting up Google API authentication...")

    # Check for credentials.json
    if not os.path.exists("credentials.json"):
        print(
            """
ERROR: credentials.json not found!

Please follow these steps:
1. Go to https://console.developers.google.com/
2. Create a new project
3. Enable the Google Calendar API and Google Tasks API
4. Create OAuth 2.0 Client ID credentials (Desktop application)
5. Download the credentials JSON file and save it as 'credentials.json' in this directory
6. Run this script again
        """
        )
        return False

    print("Found credentials.json file.")

    # Set up both Calendar and Tasks authentication
    for service in ["calendar", "tasks"]:
        token_file = f"token_{service}.json"
        creds = None

        # Load existing token if available
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_info(json.load(open(token_file)), SCOPES)

        # Refresh token if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print(f"Refreshed existing {service} token.")

        # Get new credentials if none exist
        if not creds or not creds.valid:
            print(f"\nStarting authentication flow for Google {service.capitalize()}...")
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

            # Save credentials
            with open(token_file, "w") as token:
                token.write(creds.to_json())
            print(f"Authentication for Google {service.capitalize()} completed and saved.")

    print("\nSetup completed successfully! You can now run the Task Manager Bot.")
    return True


if __name__ == "__main__":
    setup_auth()
