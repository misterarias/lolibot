import logging
import re
from lolibot.services import TaskData
from lolibot.services.middleware.protocol import TaskMiddleware


JUST_ME_PATTERNS = [
    re.compile(regex, re.IGNORECASE)
    for regex in (
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
    )
]


class JustMeInviteeMiddleware(TaskMiddleware):
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
        for pat in JUST_ME_PATTERNS:
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
