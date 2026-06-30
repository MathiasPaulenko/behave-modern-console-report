"""Shared rendering helpers for all formatters."""

from __future__ import annotations

from behave_modern_console_report.models import Execution, Feature, Scenario, Status, Step
from behave_modern_console_report.utils import format_duration


STATUS_ICON = {
    Status.PASSED: "✓",
    Status.FAILED: "✗",
    Status.SKIPPED: "⏭",
    Status.UNDEFINED: "?",
    Status.PENDING: "P",
    Status.RUNNING: "◌",
    Status.UNTESTED: " ",
}

STATUS_TEXT = {
    Status.PASSED: "passed",
    Status.FAILED: "failed",
    Status.SKIPPED: "skipped",
    Status.UNDEFINED: "undefined",
    Status.PENDING: "pending",
    Status.RUNNING: "running",
    Status.UNTESTED: "untested",
}

ANSI_COLOR = {
    Status.PASSED: "\033[32m",      # green
    Status.FAILED: "\033[31m",      # red
    Status.SKIPPED: "\033[33m",     # yellow
    Status.UNDEFINED: "\033[35m",    # magenta
    Status.PENDING: "\033[33m",     # yellow
    Status.RUNNING: "\033[90m",      # gray
    Status.UNTESTED: "\033[90m",     # gray
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
}


def colored(text: str, color: str, enabled: bool = True) -> str:
    """Wrap text in ANSI color codes if enabled."""
    if not enabled:
        return text
    code = ANSI_COLOR.get(color, "")
    return f"{code}{text}{ANSI_COLOR['reset']}"


def icon(status: Status, enabled: bool = True) -> str:
    """Return the status icon, optionally colored."""
    return colored(STATUS_ICON.get(status, " "), status.name.lower(), enabled)


def status_label(status: Status, enabled: bool = True) -> str:
    """Return a colored status label."""
    return colored(STATUS_TEXT.get(status, "?").upper(), status.name.lower(), enabled)


def status_text(status: Status) -> str:
    """Return the plain lower-case status text."""
    return STATUS_TEXT.get(status, "?")


def scenario_line(scenario: Scenario, indent: int = 2, colors: bool = True) -> str:
    """Return a single-line rendering of a scenario."""
    prefix = " " * indent
    duration = f"  ({format_duration(scenario.duration)})" if scenario.duration else ""
    return f"{prefix}{icon(scenario.status, colors)} {scenario.name}{duration}"


def step_line(step: Step, indent: int = 4, colors: bool = True) -> str:
    """Return a single-line rendering of a step."""
    prefix = " " * indent
    duration = f"  ({format_duration(step.duration)})" if step.duration else ""
    keyword = f"{step.keyword} " if step.keyword else ""
    return f"{prefix}{icon(step.status, colors)} {keyword}{step.name}{duration}"


def progress_bar(execution: Execution, width: int = 28, colors: bool = True) -> str:
    """Return a text progress bar for the current execution."""
    if execution.total_scenarios == 0:
        return ""
    filled = int(width * execution.completion_rate)
    bar = "█" * filled + "░" * (width - filled)
    percent = int(execution.completion_rate * 100)
    return f"{colored(bar, 'bold', colors)}  {percent}%  {execution.completed_scenarios} / {execution.total_scenarios} scenarios"


def summary_block(execution: Execution, colors: bool = True) -> str:
    """Return a multi-line summary block."""
    lines = [
        "",
        colored("RESULTS", "bold", colors),
        "",
        f"  {colored('Passed', 'passed', colors)}   {execution.passed_scenarios}",
        f"  {colored('Failed', 'failed', colors)}   {execution.failed_scenarios}",
        f"  {colored('Skipped', 'skipped', colors)}  {execution.skipped_scenarios}",
        "",
        f"  ⏱ Duration {format_duration(execution.duration)}",
    ]
    return "\n".join(lines)


def failures_block(execution: Execution, colors: bool = True) -> str:
    """Return a block with failure details."""
    failed = [
        (feature, scenario)
        for feature in execution.features
        for scenario in feature.scenarios
        if scenario.is_failed
    ]
    if not failed:
        return ""

    lines = ["", colored("Failures", "bold", colors)]
    for feature, scenario in failed:
        lines.append(f"\n{icon(Status.FAILED, colors)} {scenario.name}")
        lines.append(f"  Feature: {feature.name} (line {scenario.line})")
        for step in scenario.steps:
            if step.is_failed and step.error:
                lines.append(f"  {step.error.type}")
                lines.append(f"  {step.error.message}")
                if step.error.traceback:
                    lines.append(colored(step.error.traceback, "dim", colors))
    return "\n".join(lines)


def feature_header(feature: Feature, colors: bool = True) -> str:
    """Return the feature header line."""
    return f"\n{colored('Feature:', 'bold', colors)} {feature.name}"
