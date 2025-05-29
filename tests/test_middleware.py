from lolibot.services.middleware import (
    MiddlewarePipeline,
    JustMeInviteeMiddleware,
    DateValidationMiddleware,
    TitlePrefixTruncateMiddleware,
    NotTaskMiddleWare,
)
from lolibot.services import TaskData
import pytest
from datetime import datetime, timedelta

from lolibot.services.middleware.test_message_check import TestCheckerMiddleware


def test_not_task_middleware_ignores_tasks():
    mw = NotTaskMiddleWare()
    data = TaskData(task_type="event", title="Meeting", description="desc", date="2025-05-14", time="10:00", invitees=[])
    assert mw.process("msg", data) == data


def test_not_task_middleware_converts_tasks():
    mw = NotTaskMiddleWare()
    data = TaskData(task_type="task", title="Task", description="desc", date="2025-05-14", time="10:00", invitees=[])
    result = mw.process("msg", data)
    assert result.task_type == "event"


def test_not_task_middleware_ignores_tasks_with_date():
    mw = NotTaskMiddleWare()
    data = TaskData(task_type="task", title="Task", description="desc", date="2025-05-14", time=None, invitees=[])
    assert mw.process("msg", data) == data


def test_just_me_invitee_removes_invitees():
    mw = JustMeInviteeMiddleware(["default@example.com"])
    pipeline = MiddlewarePipeline([mw])
    # Message with 'just me' pattern
    msg = "Schedule a meeting just me"
    data = TaskData(
        task_type="event",
        title="Meeting",
        description="desc",
        date="2025-05-14",
        time="10:00",
        invitees=["someone@example.com"],
    )
    result = pipeline.process(msg, data)
    assert result.invitees == []


def test_just_me_invitee_spanish():
    mw = JustMeInviteeMiddleware(["default@example.com"])
    pipeline = MiddlewarePipeline([mw])
    msg = "apunta en mi calendario"
    data = TaskData(
        task_type="event",
        title="Reunión",
        description="desc",
        date="2025-05-14",
        time="10:00",
        invitees=["otro@example.com"],
    )
    result = pipeline.process(msg, data)
    assert result.invitees == []


def test_default_invitees_are_added():
    mw = JustMeInviteeMiddleware(["default@example.com"])
    pipeline = MiddlewarePipeline([mw])
    msg = "Schedule a meeting"
    data = TaskData(
        task_type="event",
        title="Meeting",
        description="desc",
        date="2025-05-14",
        time="10:00",
        invitees=None,
    )
    result = pipeline.process(msg, data)
    assert result.invitees == ["default@example.com"]


def test_no_invitees_no_changes():
    msg = "just me"
    data = TaskData(task_type="task", title="Task", description="desc", date="2025-05-14", time="10:00")
    assert JustMeInviteeMiddleware([]).process(msg, data) == data
    assert JustMeInviteeMiddleware(None).process(msg, data) == data


def test_non_event_task_type_untouched():
    mw = JustMeInviteeMiddleware(["default@example.com"])
    pipeline = MiddlewarePipeline([mw])
    msg = "just me"
    data = TaskData(
        task_type="task",
        title="Task",
        description="desc",
        date="2025-05-14",
        time="10:00",
        invitees=["someone@example.com"],
    )
    result = pipeline.process(msg, data)
    assert result.invitees == ["someone@example.com"]


def test_date_validation_middleware_valid():
    mw = DateValidationMiddleware()
    today = datetime.now().strftime("%Y-%m-%d")
    data = TaskData(
        task_type="task",
        title="T",
        description="d",
        date=today,
        time=None,
        invitees=None,
    )
    result = mw.process("msg", data)
    assert result.date == today


def test_date_validation_middleware_future():
    mw = DateValidationMiddleware()
    future = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    data = TaskData(
        task_type="task",
        title="T",
        description="d",
        date=future,
        time=None,
        invitees=None,
    )
    result = mw.process("msg", data)
    assert result.date == future


def test_date_validation_middleware_past():
    mw = DateValidationMiddleware()
    past = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    data = TaskData(
        task_type="task",
        title="T",
        description="d",
        date=past,
        time=None,
        invitees=None,
    )
    with pytest.raises(ValueError):
        mw.process("msg", data)


def test_date_validation_middleware_invalid_format():
    mw = DateValidationMiddleware()
    data = TaskData(
        task_type="task",
        title="T",
        description="d",
        date="not-a-date",
        time=None,
        invitees=None,
    )
    with pytest.raises(ValueError):
        mw.process("msg", data)


def test_title_prefix_truncate_short():
    mw = TitlePrefixTruncateMiddleware("Bot")
    data = TaskData(
        task_type="task",
        title="Short title",
        description="d",
        date=None,
        time=None,
        invitees=None,
    )
    result = mw.process("msg", data)
    assert result.title.startswith("Bot ")
    assert result.title.endswith("Short title")


def test_title_prefix_truncate_long():
    mw = TitlePrefixTruncateMiddleware("Bot")
    long_title = "A" * 60
    data = TaskData(
        task_type="task",
        title=long_title,
        description="d",
        date=None,
        time=None,
        invitees=None,
    )
    result = mw.process("msg", data)
    assert result.title.startswith("Bot ")
    assert result.title.endswith("...")
    assert len(result.title) < 70  # 50 + len("Bot ") + ...


@pytest.mark.parametrize(
    "message,expected",
    [
        ("Too short", False),
        ("Too short...", False),
        ("shorter", False),
        ("estas ahi?", False),
        ("this is a test message", True),
        ("", False),
    ],
)
def test_suspicious_words_mw(message, expected):
    mw = TestCheckerMiddleware()
    if not expected:
        with pytest.raises(ValueError):
            mw.process(message, None)
    else:
        assert mw.process(message, None) != ""
