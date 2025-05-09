"""Tests for the DefaultProvider class in the LLM module."""

import pytest
from datetime import datetime, timedelta


def get_future_date(days_ahead: int) -> str:
    """Helper function to get a future date in YYYY-MM-DD format."""
    return (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")


class TestDefaultProviderProcessText:
    """Test suite for DefaultProvider.process_text method."""

    def test_basic_task_no_date_time(self, provider):
        """Test basic task without date or time."""
        text = "Write a report"
        result = provider.process_text(text)
        assert result["task_type"] == "task"
        assert result["title"] == text
        assert result["description"] == text
        assert result["date"] == datetime.now().strftime("%Y-%m-%d")
        assert result["time"] is None

    def test_task_with_long_title(self, provider):
        """Test task with title longer than 50 characters."""
        text = "This is a very long task description that should be truncated in the title field"
        result = provider.process_text(text)
        assert len(result["title"]) <= 53  # 50 chars + "..."
        assert result["title"].endswith("...")
        assert result["description"] == text

    @pytest.mark.parametrize(
        "text,expected_type",
        [
            ("Schedule a meeting with the team", "event"),
            ("Set up a call with John", "event"),
            ("Discussion about project", "event"),
            ("Talk to marketing", "event"),
            ("Team conversation tomorrow", "event"),
            ("Remind me to call back", "reminder"),
            ("Alert me when done", "reminder"),
            ("Notify me about deadline", "reminder"),
            ("Just a regular task", "task"),
        ],
    )
    def test_task_type_detection(self, provider, text, expected_type):
        """Test different task type detection patterns."""
        result = provider.process_text(text)
        assert result["task_type"] == expected_type

    @pytest.mark.parametrize(
        "text,expected_date",
        [
            ("Do it today", datetime.now().strftime("%Y-%m-%d")),
            ("Do it tomorrow", get_future_date(1)),
            ("Meeting next monday", None),  # Will be tested separately
            ("Task on 2025-05-10", "2025-05-10"),
            ("Meeting on 5/10/2025", "2025-05-10"),
            ("Task on 15th january", None),  # Will be tested separately
        ],
    )
    def test_date_extraction(self, provider, text, expected_date):
        """Test date extraction from various formats."""
        result = provider.process_text(text)
        if expected_date:
            assert result["date"] == expected_date

    def test_next_weekday(self, provider):
        """Test 'next weekday' date extraction."""
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            text = f"Meeting next {day}"
            result = provider.process_text(text)
            # Verify the date is in the future
            result_date = datetime.strptime(result["date"], "%Y-%m-%d")
            assert result_date > datetime.now()
            assert result_date.strftime("%A").lower() == day

    @pytest.mark.parametrize(
        "text,expected_hour,expected_minute",
        [
            ("Meeting at 9:00", "09", "00"),
            ("Call at 9:00am", "09", "00"),
            ("Meeting at 9:00pm", "21", "00"),
            ("Task at 12:00am", "00", "00"),
            ("Task at 12:00pm", "12", "00"),
            ("Meeting at 15:30", "15", "30"),
            ("Call at 3:30pm", "15", "30"),
        ],
    )
    def test_time_extraction(self, provider, text, expected_hour, expected_minute):
        """Test time extraction from various formats."""
        result = provider.process_text(text)
        assert result["time"] == f"{expected_hour}:{expected_minute}"

    def test_combined_date_time_task_type(self, provider):
        """Test combining date, time, and task type detection."""
        text = "Schedule a meeting tomorrow at 3:30pm"
        result = provider.process_text(text)
        assert result["task_type"] == "event"
        assert result["date"] == get_future_date(1)
        assert result["time"] == "15:30"

    @pytest.mark.parametrize(
        "month",
        [
            "jan",
            "january",
            "feb",
            "february",
            "mar",
            "march",
            "apr",
            "april",
            "may",
            "jun",
            "june",
            "jul",
            "july",
            "aug",
            "august",
            "sep",
            "september",
            "oct",
            "october",
            "nov",
            "november",
            "dec",
            "december",
        ],
    )
    def test_month_names(self, provider, month):
        """Test recognition of various month name formats."""
        text = f"Task on 15th {month}"
        result = provider.process_text(text)
        # Just verify it extracts a date - exact date validation would need more context
        assert result["date"] is not None

    def test_invalid_time_formats(self, provider):
        """Test handling of invalid time formats."""
        invalid_times = [
            "Meeting at 25:00",  # Invalid hour
            "Task at 9:60",  # Invalid minute
        ]
        for text in invalid_times:
            result = provider.process_text(text)
            assert result["time"] is None

    def test_past_dates_handling(self, provider):
        """Test that past dates are handled appropriately."""
        # This would depend on your business logic - currently the function doesn't
        # validate if dates are in the past
        pass  # Add test based on your requirements
