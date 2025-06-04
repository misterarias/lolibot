__version__ = "1.0.4"


from dataclasses import dataclass


@dataclass(frozen=True)
class UserMessage:
    message: str
    user_id: str

    def __str__(self):
        return f"UserMessage: {self.message} (User ID: {self.user_id})"
