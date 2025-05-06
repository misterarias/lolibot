# Task Manager Bot

A personal assistant bot that helps you capture tasks, events, and reminders during meetings and throughout your workday. The bot processes natural language commands and converts them into:

- Google Tasks
- Google Calendar events
- Reminders

## Features

- Process natural language commands via a Telegram bot interface
- Automatically identify the type of request (task, event, or reminder)
- Extract relevant information like dates, times, and descriptions
- Integrate with Google Calendar and Google Tasks
- Works with various LLM providers (OpenAI, Anthropic Claude, Google Gemini)
- Fallback mode with regex parsing when no LLM is available
- Containerized for easy deployment

## Setup Instructions

### Prerequisites

1. A Telegram account
2. Google account with Calendar and Tasks enabled
3. Docker and Docker Compose installed
4. (Optional) API key for an LLM provider (OpenAI, Anthropic, or Google Gemini)

### Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat and send `/newbot` command
3. Follow the prompts to create your bot
4. Save the token provided by BotFather

### Step 2: Set up Google API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Calendar API and Google Tasks API
4. Create OAuth 2.0 Client ID credentials (Desktop application type)
5. Download the credentials JSON file and save it as `credentials.json` in the project directory

### Step 3: Configure Environment Variables

1. Copy the example environment file: `cp .env.example .env`
2. Edit `.env` and add your Telegram bot token
3. (Optional) Add your chosen LLM API key and select the provider
4. Set your timezone, e.g., `America/New_York`

### Step 4: Run the Setup Script

This script will help you authenticate with Google:

```bash
python setup_google_auth.py
```

Follow the browser prompts to authorize the application with your Google account.

### Step 5: Deploy with Docker Compose

Build and start the container:

```bash
docker-compose up -d
```

### Step 6: Start Using Your Bot

1. Open Telegram and search for your bot by username
2. Start a chat and send the `/start` command
3. The bot is now ready to process your requests!

## Usage Examples

Here are some examples of commands you can send to the bot:

- "Schedule a meeting with the design team tomorrow at 2pm"
- "Create a task to review the quarterly report by Friday"
- "Remind me to call Brian on Monday about the project status"
- "I need to submit expense reports by the end of the week"
- "Send follow-up email to marketing team after lunch"

## LLM Provider Options

The bot supports three LLM providers:

1. **OpenAI (default)** - Uses GPT models for natural language processing
2. **Anthropic** - Uses Claude models
3. **Google Gemini** - Uses Google's Gemini models

If no LLM API key is provided, the bot will use a regex-based fallback parser.

## Maintenance and Troubleshooting

### Checking Logs

```bash
docker-compose logs -f taskbot
```

### Restarting the Bot

```bash
docker-compose restart taskbot
```

### Updating the Bot

```bash
git pull
docker-compose down
docker-compose up -d --build
```

## Directory Structure

- `app.py` - Main application code
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Service deployment configuration
- `requirements.txt` - Python dependencies
- `setup_google_auth.py` - Google API authentication setup
- `credentials.json` - Google API credentials (you need to create this)
- `token_calendar.json` - Google Calendar API token (created during setup)
- `token_tasks.json` - Google Tasks API token (created during setup)
- `.env` - Environment variables configuration
- `data/` - Directory for persistent data storage

## Security Notes

- The `.env` file contains sensitive API keys - never commit it to version control
- OAuth tokens for Google services are stored in the `token_*.json` files
- All data is stored locally and processed through your own API keys

## Advanced Configuration

For more advanced configuration options, you can:

1. Modify the `app.py` file to add custom parsing rules
2. Adjust the Docker Compose configuration for resource limits
3. Implement additional Google API integrations

## License

This project is open source and available under the MIT License.