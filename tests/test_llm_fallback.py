import pytest
from lolibot.llm.processor import LLMProcessor
from lolibot.config import BotConfig


class DummyProvider:
    def __init__(self, config):
        pass

    def name(self):
        return "Dummy"

    def process_text(self, text):
        raise Exception("fail")

    def check_connection(self):
        return False


class DummyDefault:
    def __init__(self, config):
        pass

    def process_text(self, text):
        return {"fallback": True}


@pytest.fixture
def config():
    return BotConfig(
        bot_name="TestBot",
        default_timezone="UTC",
        context_name="default",
        openai_api_key="k",
        gemini_api_key="k",
        claude_api_key="k",
        telegram_bot_token="t",
        available_contexts=["default"],
        config_path=None,
    )


def test_llmprocessor_fallback(monkeypatch, config):
    # All providers fail, should fallback to default
    monkeypatch.setattr("lolibot.llm.processor.OpenAIProvider", lambda c: DummyProvider(c))
    monkeypatch.setattr("lolibot.llm.processor.AnthropicProvider", lambda c: DummyProvider(c))
    monkeypatch.setattr("lolibot.llm.processor.GeminiProvider", lambda c: DummyProvider(c))
    monkeypatch.setattr("lolibot.llm.processor.DefaultProvider", lambda c: DummyDefault(c))
    proc = LLMProcessor(config)
    result = proc.process_text("hi")
    assert result["fallback"] is True


def test_llmprocessor_first_success(monkeypatch, config):
    class SuccessProvider:
        def __init__(self, config):
            pass

        def name(self):
            return "Success"

        def process_text(self, text):
            return {"ok": True}

        def check_connection(self):
            return True

    monkeypatch.setattr("lolibot.llm.processor.OpenAIProvider", lambda c: SuccessProvider(c))
    monkeypatch.setattr("lolibot.llm.processor.AnthropicProvider", lambda c: DummyProvider(c))
    monkeypatch.setattr("lolibot.llm.processor.GeminiProvider", lambda c: DummyProvider(c))
    monkeypatch.setattr("lolibot.llm.processor.DefaultProvider", lambda c: DummyDefault(c))
    proc = LLMProcessor(config)
    result = proc.process_text("hi")
    assert result["ok"] is True
