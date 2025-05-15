from lolibot.llm.prompts import common_prompt


def test_common_prompt_default():
    prompt = common_prompt()
    assert "Extract information" in prompt
    assert "task_type" in prompt
    assert "date" in prompt
    assert "time" in prompt


def test_common_prompt_with_text():
    text = "Remind me to call John tomorrow"
    prompt = common_prompt(text)
    assert text in prompt
    assert "Extract information from this message" in prompt
