"""Tests for utility functions."""

from behave_modern_console_report.utils import estimate_remaining, format_duration


def test_format_duration_sub_second() -> None:
    assert format_duration(0.42) == "420ms"


def test_format_duration_seconds() -> None:
    assert format_duration(12.5) == "12.5s"


def test_format_duration_minutes() -> None:
    assert format_duration(222.0) == "3m42s"


def test_format_duration_hours() -> None:
    assert format_duration(3665.0) == "1h01m05s"


def test_format_duration_zero() -> None:
    assert format_duration(0.0) == "0ms"


def test_format_duration_micro() -> None:
    assert format_duration(0.00004) == "0ms"


def test_estimate_remaining_basic() -> None:
    remaining = estimate_remaining(10.0, 5, 10)
    assert remaining == 10.0


def test_estimate_remaining_none_when_no_progress() -> None:
    assert estimate_remaining(1.0, 0, 10) is None


def test_estimate_remaining_none_when_finished() -> None:
    assert estimate_remaining(10.0, 10, 10) is None
