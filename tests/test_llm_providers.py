from lolibot.llm import LLMProvider, OpenAIProvider, AnthropicProvider, GeminiProvider, DefaultProvider
from lolibot.config import BotConfig


def make_config():
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


def test_llm_provider_abstract_methods():
    class Dummy(LLMProvider):
        def __init__(self, config):
            pass

        def name(self):
            return "Dummy"

        def process_text(self, text):
            return {"ok": True}

        def check_connection(self):
            return True

    d = Dummy(make_config())
    assert d.name() == "Dummy"
    assert d.process_text("hi")["ok"]
    assert d.check_connection()


def test_default_provider_check_connection():
    p = DefaultProvider(make_config())
    assert p.check_connection()


def test_openai_provider_name():
    p = OpenAIProvider(make_config())
    assert p.name() == "OpenAI"


def test_anthropic_provider_name():
    p = AnthropicProvider(make_config())
    assert p.name() == "Anthropic"


def test_gemini_provider_name():
    p = GeminiProvider(make_config())
    assert p.name() == "Gemini"
