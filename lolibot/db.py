"""Database handling module for the Task Manager Bot."""
import logging
import sqlite3
from lolibot.config import DB_PATH

logger = logging.getLogger(__name__)


def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    logger.debug("Initializing database...")
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        message TEXT,
        task_type TEXT,
        task_title TEXT,
        task_description TEXT,
        task_date TEXT,
        task_time TEXT,
        google_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed BOOLEAN DEFAULT FALSE
    )
    """
    )
    conn.commit()
    conn.close()


def save_task_to_db(user_id, message, task_data, google_id=None):
    """Save task information to the local database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    logger.debug("Saving task to database...")

    cursor.execute(
        """
        INSERT INTO tasks (
            user_id, message, task_type, task_title, task_description,
            task_date, task_time, google_id, processed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            message,
            task_data["task_type"],
            task_data["title"],
            task_data["description"],
            task_data["date"],
            task_data["time"],
            google_id,
            bool(google_id),
        ),
    )
    logger.debug("Task saved to database with ID: %s", cursor.lastrowid)

    conn.commit()
    conn.close()
