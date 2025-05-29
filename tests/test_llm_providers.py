from lolibot.llm import LLMProvider, OpenAIProvider, AnthropicProvider, GeminiProvider, DefaultProvider


def test_llm_provider_abstract_methods(test_config):
    class Dummy(LLMProvider):
        def __init__(self, config):
            pass

        def name(self):
            return "Dummy"

        def process_text(self, text):
            return {"ok": True}

        def check_connection(self):
            return True

        def enabled(self):
            return False

    d = Dummy(test_config)
    assert d.name() == "Dummy"
    assert d.process_text("hi")["ok"]
    assert d.check_connection()
    assert not d.enabled()


def test_default_provider_check_connection(test_config):
    p = DefaultProvider(test_config)
    assert p.check_connection()


def test_openai_provider_name(test_config):
    p = OpenAIProvider(test_config)
    assert p.name() == "OpenAI"


def test_anthropic_provider_name(test_config):
    p = AnthropicProvider(test_config)
    assert p.name() == "Anthropic"


def test_gemini_provider_name(test_config):
    p = GeminiProvider(test_config)
    assert p.name() == "Gemini Flash 2.5"
