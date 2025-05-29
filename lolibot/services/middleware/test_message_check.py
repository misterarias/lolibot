from lolibot.services import TaskData


class TestCheckerMiddleware:
    PUNCTUATION_MARKS = {".", ",", "!", "?", ";", ":"}

    def process(self, message: str, data: TaskData) -> TaskData:
        words = message.split()
        cleaned_words = set(filter(lambda w: w not in self.PUNCTUATION_MARKS, words))
        if len(cleaned_words) < 3:
            raise ValueError("Message is too short, it must contain at least 3 words.")

        return data
