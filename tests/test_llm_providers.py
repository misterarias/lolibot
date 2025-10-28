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

        def split_text(self, text) -> list:
            return [text]

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


def test_default_provider_split_text(test_config):
    p = DefaultProvider(test_config)
    text = "This is a test."
    chunks = p.split_text(text)
    assert chunks == [text]


def test_split_task_with_comma(test_config):
    text = "Buy milk, call mom, send email"
    p = DefaultProvider(test_config)
    segments = p.split_text(text)
    assert len(segments) == 3
    assert "Buy milk" in segments
    assert "call mom" in segments
    assert "send email" in segments


def test_split_task_with_spanish_y(test_config):
    text = "Comprar leche y llamar a mamá y enviar email"
    p = DefaultProvider(test_config)
    segments = p.split_text(text)

    assert len(segments) == 3
    assert "Comprar leche" in segments
    assert "llamar a mamá" in segments
    assert "enviar email" in segments


def test_split_task_with_english_and(test_config):
    text = "Buy milk and call mom and send email"
    p = DefaultProvider(test_config)
    segments = p.split_text(text)

    assert len(segments) == 3
    assert "Buy milk" in segments
    assert "call mom" in segments
    assert "send email" in segments


def test_split_task_preserves_time(test_config):
    text = "Meeting at 10:30, call mom at 11:15"
    p = DefaultProvider(test_config)
    segments = p.split_text(text)

    assert len(segments) == 2
    assert "Meeting at 10:30" in segments
    assert "call mom at 11:15" in segments


def test_support_multilingual_separators(test_config):
    text = "Buy milk y call mom, enviar email además " "schedule meeting and send report also create task"
    p = DefaultProvider(test_config)
    segments = p.split_text(text)

    assert len(segments) == 6  # Fixed: The expected list had 6 items
    expected = ["Buy milk", "call mom", "enviar email", "schedule meeting", "send report", "create task"]
    assert len(expected) == len(segments)
    for task in expected:
        assert any(task in segment for segment in segments)
