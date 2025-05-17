"""Database handling module for the Task Manager Bot."""

import logging
import sqlite3
import os

from lolibot.services import TaskData

logger = logging.getLogger(__name__)


def get_db_path():
    """Get the path to the SQLite database."""
    return os.getenv("DB_PATH", "./taskbot.db")


def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(get_db_path())
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
        result_ok BOOLEAN DEFAUL FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed BOOLEAN DEFAULT FALSE
    )
    """
    )
    conn.commit()
    conn.close()


def save_task_to_db(user_id, message, task_data: TaskData, result_ok=False):
    """Save task information to the local database."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    logger.debug("Saving task to database...")

    cursor.execute(
        """
        INSERT INTO tasks (
            user_id, message, task_type, task_title, task_description,
            task_date, task_time, processed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, message, task_data.task_type, task_data.title, task_data.description, task_data.date, task_data.time, result_ok),
    )
    logger.debug("Task saved to database with ID: %s", cursor.lastrowid)

    conn.commit()
    conn.close()
