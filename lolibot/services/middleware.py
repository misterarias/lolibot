"""Middleware layer for pre-processing task/event/reminder data before TaskManager."""

import logging
from typing import Protocol, List
from lolibot.services import TaskData
import re
from datetime import datetime


class TaskMiddleware(Protocol):
    def process(self, message: str, data: TaskData) -> TaskData: ...


class MiddlewarePipeline:
    def __init__(self, middlewares: List[TaskMiddleware]):
        self.middlewares = middlewares

    def process(self, message: str, data: TaskData) -> TaskData:
        for mw in self.middlewares:
            data = mw.process(message, data)
        return data


class JustMeInviteeMiddleware:
    JUST_ME_PATTERNS = [
        r"just me",
        r"only me",
        r"myself",
        r"solo a mi",
        r"solamente a mi",
        r"apunta en mi calendario",
        r"sólo a mí",
        r"sólo para mí",
        r"sólo yo",
        r"solo yo",
        r"para mí solo",
        r"para mi solo",
        r"en mi calendario",
        r"sólo en mi calendario",
        r"only in my calendar",
        r"add to my calendar",
        r"apúntalo sólo para mí",
        r"apúntalo solo para mí",
        r"apúntalo en mi calendario",
        r"apúntame",
        r"ponlo sólo para mí",
        r"ponlo solo para mí",
        r"ponlo en mi calendario",
    ]

    def __init__(self, default_invitees: list):
        self.default_invitees = default_invitees
        self.logger = logging.getLogger(__name__)

    def process(self, message: str, data: TaskData) -> TaskData:
        if data.task_type != "event":
            # If the task type is not an event, do not modify invitees
            return data

        if len(self.default_invitees) == 0:
            # No default invitees, return data as is
            return data

        msg = message.lower()
        for pat in self.JUST_ME_PATTERNS:
            if re.search(pat, msg):
                # Remove invitees
                self.logger.info(f"Keyword '{pat}' matched. Setting invitees to empty list.")
                return TaskData(
                    task_type=data.task_type,
                    title=data.title,
                    description=data.description,
                    date=data.date,
                    time=data.time,
                    invitees=[],
                )

        # If no "just me" pattern matched, add default invitees
        return TaskData(
            task_type=data.task_type,
            title=data.title,
            description=data.description,
            date=data.date,
            time=data.time,
            invitees=self.default_invitees,
        )


class DateValidationMiddleware:
    def process(self, message: str, data: TaskData) -> TaskData:
        if data.date:
            try:
                task_date = datetime.strptime(data.date, "%Y-%m-%d").date()
                if task_date < datetime.now().date():
                    raise ValueError("Task date cannot be in the past.")
            except ValueError as e:
                raise ValueError(f"Invalid date format: {e}")
        return data


class TitlePrefixTruncateMiddleware:
    def __init__(self, bot_name: str):
        self.bot_name = bot_name

    def process(self, message: str, data: TaskData) -> TaskData:
        title = data.title
        if len(title) > 50:
            title = title[:50] + "..."
        title = f"{self.bot_name} {title}"
        return TaskData(
            task_type=data.task_type,
            title=title,
            description=data.description,
            date=data.date,
            time=data.time,
            invitees=data.invitees,
        )
