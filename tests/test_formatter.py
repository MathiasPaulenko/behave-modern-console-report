"""Tests for the Behave formatter entry point."""

from __future__ import annotations

import io

from behave.formatter.base import StreamOpener

from behave_modern_console_report.formatter import ModernConsoleFormatter
from tests.conftest import FakeBehaveConfig, FakeFeature, FakeScenario, FakeStep


def make_formatter(user_data: dict[str, str] | None = None) -> ModernConsoleFormatter:
    stream = io.StringIO()
    opener = StreamOpener(stream=stream)
    config = FakeBehaveConfig(user_data=user_data or {})
    return ModernConsoleFormatter(opener, config)


def test_formatter_with_passed_scenario() -> None:
    formatter = make_formatter({"modern_console_colors": "false"})
    feature = FakeFeature(name="Authentication")
    scenario = FakeScenario(name="User logs in")
    step = FakeStep(name="user is on the login page")
    result = FakeStep(status="passed", duration=0.1)

    formatter.feature(feature)
    formatter.scenario(scenario)
    formatter.step(step)
    formatter.match(None)
    formatter.result(result)
    formatter.close()

    output = formatter._console_manager.console.file.getvalue()
    assert "Behave Modern Console Report" in output
    assert "User logs in" in output
    assert "Passed   1" in output
    assert "Failed   0" in output


def test_formatter_with_failed_scenario() -> None:
    formatter = make_formatter({"modern_console_colors": "false"})
    feature = FakeFeature(name="Checkout")
    scenario = FakeScenario(name="Payment fails")
    step = FakeStep(name="user submits payment")
    result = FakeStep(
        status="failed",
        duration=0.2,
        error_message="AssertionError: Expected 200\nActual 500",
    )

    formatter.feature(feature)
    formatter.scenario(scenario)
    formatter.step(step)
    formatter.match(None)
    formatter.result(result)
    formatter.close()

    output = formatter._console_manager.console.file.getvalue()
    assert "Payment fails" in output
    assert "AssertionError" in output
    assert "Expected 200" in output
    assert "Failed   1" in output


def test_formatter_minimal_verbosity() -> None:
    formatter = make_formatter(
        {
            "modern_console_colors": "false",
            "modern_console_verbosity": "minimal",
        }
    )
    feature = FakeFeature()
    scenario = FakeScenario(name="S1")
    step = FakeStep()
    result = FakeStep(status="passed", duration=0.1)

    formatter.feature(feature)
    formatter.scenario(scenario)
    formatter.step(step)
    formatter.match(None)
    formatter.result(result)
    formatter.close()

    output = formatter._console_manager.console.file.getvalue()
    assert "RESULTS" in output
    assert "Behave Modern Console Report" not in output


def test_formatter_golden_output_snapshot() -> None:
    """Golden snapshot test for a small mixed execution."""
    formatter = make_formatter(
        {
            "modern_console_colors": "false",
            "modern_console_show_progress": "false",
        }
    )

    formatter.feature(FakeFeature(name="E-commerce"))
    for scenario_name, status, error in [
        ("Login", "passed", None),
        ("Register", "passed", None),
        ("Checkout", "failed", "AssertionError: Expected 200\nActual 500"),
    ]:
        formatter.scenario(FakeScenario(name=scenario_name))
        formatter.step(FakeStep(name=f"run {scenario_name.lower()}"))
        formatter.match(None)
        result = FakeStep(
            status=status,
            duration=0.1,
            error_message=error or "",
        )
        formatter.result(result)

    formatter.close()

    output = formatter._console_manager.console.file.getvalue()
    assert "E-commerce" in output
    assert "Login" in output
    assert "Register" in output
    assert "Checkout" in output
    assert "Passed   2" in output
    assert "Failed   1" in output
    assert "Duration" in output
