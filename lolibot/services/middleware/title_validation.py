from lolibot.services import TaskData


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
