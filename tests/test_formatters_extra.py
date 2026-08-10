"""Tests for CI, Log, Minimal, and Progress formatters."""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

from behave.formatter.base import StreamOpener

from behave_modern_console_report.formatters.ci import CIFormatter
from behave_modern_console_report.formatters.log import LogFormatter
from behave_modern_console_report.formatters.minimal import MinimalFormatter
from behave_modern_console_report.formatters.progress import ProgressFormatter
from tests.conftest import FakeFeature, FakeScenario, FakeStep

if TYPE_CHECKING:
    from behave_modern_console_report.base import BaseFormatter


def _make_formatter(
    cls: type[BaseFormatter], user_data: dict[str, str] | None = None
) -> BaseFormatter:
    stream = io.StringIO()
    opener = StreamOpener(stream=stream)
    config = type("Config", (), {"userdata": user_data or {}})()
    return cls(opener, config)


def _run_scenario(
    formatter: BaseFormatter,
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


# --- MinimalFormatter ---


def test_minimal_formatter_passed_scenario() -> None:
    formatter = _make_formatter(MinimalFormatter, {"mcr.colors": "false"})
    _run_scenario(formatter, "Auth", "User logs in", "passed")
    formatter.close()
    output = formatter._stream.getvalue()
    assert "[PASSED]" in output
    assert "User logs in" in output
    assert "Passed 1" in output


def test_minimal_formatter_failed_scenario() -> None:
    formatter = _make_formatter(MinimalFormatter, {"mcr.colors": "false"})
    _run_scenario(formatter, "Auth", "Login fails", "failed", "AssertionError: bad")
    formatter.close()
    output = formatter._stream.getvalue()
    assert "[FAILED]" in output
    assert "Failed 1" in output


def test_minimal_formatter_skipped_scenario() -> None:
    formatter = _make_formatter(MinimalFormatter, {"mcr.colors": "false"})
    formatter.feature(FakeFeature(name="Auth"))
    formatter.scenario(FakeScenario(name="Skipped scenario", status="skipped"))
    formatter.close()
    output = formatter._stream.getvalue()
    assert "[SKIPPED]" in output
    assert "Skipped 1" in output


# --- CIFormatter ---


def test_ci_formatter_passed_scenario() -> None:
    formatter = _make_formatter(CIFormatter, {"mcr.colors": "false"})
    _run_scenario(formatter, "Auth", "User logs in", "passed")
    formatter.close()
    output = formatter._stream.getvalue()
    assert "[PASSED]" in output
    assert "User logs in" in output
    assert "Passed" in output


def test_ci_formatter_failed_scenario() -> None:
    formatter = _make_formatter(CIFormatter, {"mcr.colors": "false"})
    _run_scenario(
        formatter,
        "Checkout",
        "Payment fails",
        "failed",
        "AssertionError: Expected 200\nActual 500",
    )
    formatter.close()
    output = formatter._stream.getvalue()
    assert "[FAILED]" in output
    assert "Payment fails" in output
    assert "Failed" in output


def test_ci_formatter_undefined_scenario() -> None:
    formatter = _make_formatter(CIFormatter, {"mcr.colors": "false"})
    _run_scenario(formatter, "Auth", "Unknown step", "undefined")
    formatter.close()
    output = formatter._stream.getvalue()
    assert "[UNDEFINED]" in output
    assert "Undefined" in output


# --- LogFormatter ---


def test_log_formatter_passed_scenario() -> None:
    formatter = _make_formatter(LogFormatter, {"mcr.colors": "false"})
    _run_scenario(formatter, "Auth", "User logs in", "passed")
    formatter.close()
    output = formatter._stream.getvalue()
    assert "Feature: Auth" in output
    assert "[PASSED]" in output
    assert "User logs in" in output
    assert "Passed:" in output


def test_log_formatter_failed_scenario() -> None:
    formatter = _make_formatter(LogFormatter, {"mcr.colors": "false"})
    _run_scenario(
        formatter,
        "Checkout",
        "Payment fails",
        "failed",
        "AssertionError: bad request",
    )
    formatter.close()
    output = formatter._stream.getvalue()
    assert "[FAILED]" in output
    assert "Payment fails" in output
    assert "Failed:" in output
    assert "ERROR:" in output


def test_log_formatter_execution_finished() -> None:
    formatter = _make_formatter(LogFormatter, {"mcr.colors": "false"})
    _run_scenario(formatter, "Auth", "User logs in", "passed")
    formatter.close()
    output = formatter._stream.getvalue()
    assert "Execution finished" in output


# --- ProgressFormatter ---


def test_progress_formatter_basic() -> None:
    formatter = _make_formatter(ProgressFormatter, {"mcr.colors": "false"})
    _run_scenario(formatter, "Auth", "User logs in", "passed")
    formatter.close()
    output = formatter._stream.getvalue()
    assert "Passed 1" in output
    assert "Duration" in output


def test_progress_formatter_no_scenarios() -> None:
    formatter = _make_formatter(ProgressFormatter, {"mcr.colors": "false"})
    formatter.close()
    output = formatter._stream.getvalue()
    assert "Passed 0" in output


def test_progress_formatter_multiple_scenarios() -> None:
    formatter = _make_formatter(ProgressFormatter, {"mcr.colors": "false"})
    _run_scenario(formatter, "Auth", "Login", "passed")
    _run_scenario(formatter, "Auth", "Logout", "passed")
    formatter.close()
    output = formatter._stream.getvalue()
    assert "Passed 2" in output


def test_progress_formatter_uses_base_stream() -> None:
    """Regression: ProgressFormatter must use self._stream (opened by BaseFormatter),
    not call stream.open() a second time which could produce a different stream."""
    formatter = _make_formatter(ProgressFormatter, {"mcr.colors": "false"})
    assert formatter._actual_stream is formatter._stream


# --- Edge cases ---


def test_close_idempotent() -> None:
    """Calling close() twice should not duplicate output or crash."""
    formatter = _make_formatter(MinimalFormatter, {"mcr.colors": "false"})
    _run_scenario(formatter, "Auth", "Login", "passed")
    formatter.close()
    first_output = formatter._stream.getvalue()
    formatter.close()
    second_output = formatter._stream.getvalue()
    assert first_output == second_output


def test_formatter_without_any_scenarios() -> None:
    """Formatter should handle zero scenarios gracefully."""
    formatter = _make_formatter(CIFormatter, {"mcr.colors": "false"})
    formatter.close()
    output = formatter._stream.getvalue()
    assert "Passed" in output
    assert "Duration" in output


def test_formatter_step_without_match() -> None:
    """A step result without a prior match should not crash."""
    formatter = _make_formatter(MinimalFormatter, {"mcr.colors": "false"})
    formatter.feature(FakeFeature(name="Auth"))
    formatter.scenario(FakeScenario(name="Login"))
    formatter.step(FakeStep(name="click button"))
    # No match() call — result should still work
    formatter.result(FakeStep(status="passed", duration=0.1))
    formatter.close()
    output = formatter._stream.getvalue()
    assert "Login" in output
