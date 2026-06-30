"""Shared rendering helpers using Rich text objects.

Rich text objects let the Console render colors correctly on Windows through
its legacy console API, avoiding the need for raw ANSI escape codes.
"""

from __future__ import annotations

from rich.text import Text

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

STATUS_STYLE = {
    Status.PASSED: "green",
    Status.FAILED: "red",
    Status.SKIPPED: "yellow",
    Status.UNDEFINED: "magenta",
    Status.PENDING: "yellow",
    Status.RUNNING: "dim",
    Status.UNTESTED: "dim",
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


def icon(status: Status) -> Text:
    """Return the status icon as a styled Text object."""
    return Text(STATUS_ICON.get(status, " "), style=STATUS_STYLE.get(status, "default"))


def status_text(status: Status) -> str:
    """Return the plain lower-case status text."""
    return STATUS_TEXT.get(status, "?")


def status_label(status: Status) -> Text:
    """Return a styled status label."""
    return Text(STATUS_TEXT.get(status, "?").upper(), style=STATUS_STYLE.get(status, "default"))


def scenario_line(scenario: Scenario, indent: int = 2) -> Text:
    """Return a styled Text line for a scenario."""
    line = Text(" " * indent)
    line.append_text(icon(scenario.status))
    line.append(f" {scenario.name}")
    if scenario.duration:
        line.append(f"  ({format_duration(scenario.duration)})", style="dim")
    return line


def step_line(step: Step, indent: int = 4) -> Text:
    """Return a styled Text line for a step."""
    line = Text(" " * indent)
    line.append_text(icon(step.status))
    keyword = f"{step.keyword} " if step.keyword else ""
    line.append(f" {keyword}{step.name}")
    if step.duration:
        line.append(f"  ({format_duration(step.duration)})", style="dim")
    return line


def progress_bar(execution: Execution, width: int = 28) -> Text:
    """Return a styled Text progress bar for the execution."""
    if execution.total_scenarios == 0:
        return Text("")
    filled = int(width * execution.completion_rate)
    bar = Text("█" * filled + "░" * (width - filled), style="bold")
    percent = int(execution.completion_rate * 100)
    bar.append(f"  {percent}%  {execution.completed_scenarios} / {execution.total_scenarios} scenarios")
    return bar


def summary_block(execution: Execution) -> Text:
    """Return a styled Text summary block."""
    lines = Text()
    lines.append("\n")
    lines.append("RESULTS\n", style="bold")
    lines.append("\n")
    lines.append_text(Text("  Passed   ", style="green"))
    lines.append(f"{execution.passed_scenarios}\n")
    lines.append_text(Text("  Failed   ", style="red"))
    lines.append(f"{execution.failed_scenarios}\n")
    lines.append_text(Text("  Skipped  ", style="yellow"))
    lines.append(f"{execution.skipped_scenarios}\n")
    lines.append("\n")
    lines.append(f"  ⏱ Duration {format_duration(execution.duration)}\n")
    return lines


def failures_block(execution: Execution) -> Text:
    """Return a styled Text block with failure details."""
    failed = [
        (feature, scenario)
        for feature in execution.features
        for scenario in feature.scenarios
        if scenario.is_failed
    ]
    if not failed:
        return Text("")

    lines = Text()
    lines.append("\n")
    lines.append("Failures\n", style="bold")
    for feature, scenario in failed:
        lines.append("\n")
        lines.append_text(icon(Status.FAILED))
        lines.append(f" {scenario.name}\n")
        lines.append(f"  Feature: {feature.name} (line {scenario.line})\n")
        for step in scenario.steps:
            if step.is_failed and step.error:
                lines.append(f"  {step.error.type}\n")
                lines.append(f"  {step.error.message}\n")
                if step.error.traceback:
                    lines.append_text(Text(step.error.traceback, style="dim"))
                    lines.append("\n")
    return lines


def feature_header(feature: Feature) -> Text:
    """Return the styled feature header."""
    return Text.assemble(("\nFeature: ", "bold"), (feature.name, ""))
