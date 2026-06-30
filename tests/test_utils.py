"""Tests for utility functions."""

from behave_modern_console_report.utils import format_duration


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
