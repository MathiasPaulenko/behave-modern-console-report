"""Tests for the modern formatter."""

from __future__ import annotations

import io

from behave.formatter.base import StreamOpener

from behave_modern_console_report.formatters.modern import ModernFormatter
from tests.conftest import FakeFeature, FakeScenario, FakeStep


def make_formatter(user_data: dict[str, str] | None = None) -> ModernFormatter:
    stream = io.StringIO()
    opener = StreamOpener(stream=stream)
    config = type("Config", (), {"userdata": user_data or {}})()
    return ModernFormatter(opener, config)


def _run_scenario(
    formatter: ModernFormatter,
    feature_name: str,
    scenario_name: str,
    status: str,
    error: str = "",
) -> None:
    formatter.feature(FakeFeature(name=feature_name))
    formatter.scenario(FakeScenario(name=scenario_name))
    formatter.step(FakeStep(name=f"run {scenario_name.lower()}"))
    formatter.match(None)
    formatter.result(FakeStep(status=status, duration=0.1, error_message=error))


def test_formatter_with_passed_scenario() -> None:
    formatter = make_formatter({"mcr.colors": "false"})
    _run_scenario(formatter, "Authentication", "User logs in", "passed")
    formatter.close()

    output = formatter._stream.getvalue()
    assert "Behave Modern Console Report" in output
    assert "User logs in" in output
    assert "Passed   1" in output


def test_formatter_with_failed_scenario() -> None:
    formatter = make_formatter({"mcr.colors": "false"})
    _run_scenario(
        formatter,
        "Checkout",
        "Payment fails",
        "failed",
        "AssertionError: Expected 200\nActual 500",
    )
    formatter.close()

    output = formatter._stream.getvalue()
    assert "Payment fails" in output
    assert "AssertionError" in output
    assert "Expected 200" in output
    assert "Failed   1" in output


def test_formatter_failed_scenario_without_error_type() -> None:
    """Regression: failures_block should not print a blank line for empty error type."""
    formatter = make_formatter({"mcr.colors": "false"})
    _run_scenario(
        formatter,
        "Checkout",
        "Payment fails",
        "failed",
        "Something went wrong",
    )
    formatter.close()

    output = formatter._stream.getvalue()
    assert "Payment fails" in output
    assert "Something went wrong" in output
    lines = output.splitlines()
    assert not any(
        line.strip() == "" and i > 0 and "Feature:" in lines[i - 1] for i, line in enumerate(lines)
    )


def test_formatter_golden_output() -> None:
    formatter = make_formatter({"mcr.colors": "false"})

    for scenario_name, status, error in [
        ("Login", "passed", ""),
        ("Register", "passed", ""),
        ("Checkout", "failed", "AssertionError: Expected 200\nActual 500"),
    ]:
        _run_scenario(formatter, "E-commerce", scenario_name, status, error)

    formatter.close()

    output = formatter._stream.getvalue()
    assert "E-commerce" in output
    assert "Login" in output
    assert "Register" in output
    assert "Checkout" in output
    assert "Passed   2" in output
    assert "Failed   1" in output
    assert "Duration" in output


def test_formatter_with_undefined_scenario() -> None:
    """Regression: UNDEFINED scenarios should be counted and displayed in summary."""
    formatter = make_formatter({"mcr.colors": "false"})

    for scenario_name, status, error in [
        ("Login", "passed", ""),
        ("Register", "undefined", ""),
    ]:
        _run_scenario(formatter, "E-commerce", scenario_name, status, error)

    formatter.close()

    output = formatter._stream.getvalue()
    assert "Passed   1" in output
    assert "Undefined" in output
    assert "1" in output
