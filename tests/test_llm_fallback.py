from lolibot.llm.processor import LLMProcessor


class DummyProvider:
    def __init__(self, config):
        pass

    def name(self):
        return "Dummy"

    def process_text(self, text):
        raise Exception("fail")

    def check_connection(self):
        return False

    def enabled(self):
        return True


class DummyDefault:
    def __init__(self, config):
        pass

    def process_text(self, text):
        return {"fallback": True}


def test_llmprocessor_fallback(monkeypatch, test_config):
    # All providers fail, should fallback to default
    monkeypatch.setattr("lolibot.llm.processor.OpenAIProvider", lambda c: DummyProvider(c))
    monkeypatch.setattr("lolibot.llm.processor.AnthropicProvider", lambda c: DummyProvider(c))
    monkeypatch.setattr("lolibot.llm.processor.GeminiProvider", lambda c: DummyProvider(c))
    monkeypatch.setattr("lolibot.llm.processor.DefaultProvider", lambda c: DummyDefault(c))

    proc = LLMProcessor(test_config)
    result = proc.process_text("hi")
    assert result["fallback"] is True


def test_llmprocessor_first_success(monkeypatch, test_config):
    class SuccessProvider:
        def __init__(self, config):
            pass

        def name(self):
            return "Success"

        def process_text(self, text):
            return {"ok": True}

        def check_connection(self):
            return True

        def enabled(self):
            return True

    monkeypatch.setattr("lolibot.llm.processor.OpenAIProvider", lambda c: SuccessProvider(c))
    monkeypatch.setattr("lolibot.llm.processor.AnthropicProvider", lambda c: DummyProvider(c))
    monkeypatch.setattr("lolibot.llm.processor.GeminiProvider", lambda c: DummyProvider(c))
    monkeypatch.setattr("lolibot.llm.processor.DefaultProvider", lambda c: DummyDefault(c))
    proc = LLMProcessor(test_config)
    result = proc.process_text("hi")
    assert result["ok"] is True
