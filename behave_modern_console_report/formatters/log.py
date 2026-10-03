"""Plain log-style formatter."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any

from rich.text import Text

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import status_text
from behave_modern_console_report.utils import format_duration

if TYPE_CHECKING:
    from behave_modern_console_report.models import Scenario


def _timestamp() -> str:
    """Return an ISO-like timestamp for log lines."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class LogFormatter(BaseFormatter):
    """Formatter that prints every completed event as a timestamped log line."""

    name = "log"
    description = "Timestamped log output for every completed feature/scenario/step"

    def __init__(self, stream: Any, config: Any) -> None:
        super().__init__(stream, config)
        self._printed_scenarios: set[int] = set()
        self._printed_steps: set[int] = set()

    def feature(self, feature: Any) -> None:
        super().feature(feature)
        self._console.print(f"[{_timestamp()}] Feature: {feature.name}")

    def _emit_scenario(self, scenario: Scenario) -> None:
        """Print a scenario line and its steps (first time only)."""
        cfg = self.formatter_config
        self._printed_scenarios.add(id(scenario))
        line = Text(f"[{_timestamp()}] ")
        line.append(
            f"[{scenario.status.name.upper()}]",
            style=self._status_style(scenario.status.name),
        )
        line.append(
            f" Scenario {status_text(scenario.status)}: {scenario.name} "
            f"({format_duration(scenario.duration)})"
        )
        self._console.print(line)
        if cfg.show_steps:
            for step in scenario.steps:
                if id(step) in self._printed_steps:
                    continue
                self._printed_steps.add(id(step))
                step_text = Text(f"[{_timestamp()}]   ")
                step_text.append(
                    f"[{step.status.name.upper()}]",
                    style=self._status_style(step.status.name),
                )
                step_text.append(
                    f" Step {status_text(step.status)}: {step.keyword} {step.name} "
                    f"({format_duration(step.duration)})"
                )
                self._console.print(step_text)
                if step.is_failed and step.error and cfg.show_traceback:
                    error_line = Text(f"[{_timestamp()}]     ")
                    error_line.append("ERROR:", style="red")
                    error_line.append(f" {step.error.message}")
                    self._console.print(error_line)

    def _emit_pending(self) -> None:
        """Print all terminal scenarios that have not been emitted yet."""
        for feature in self._collector.execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal and id(scenario) not in self._printed_scenarios:
                    self._emit_scenario(scenario)

    def on_result(self) -> None:
        self._emit_pending()

    def _status_style(self, status: str) -> str:
        status = status.lower()
        if status == "passed":
            return "green"
        if status == "skipped":
            return "blue"
        if status == "failed":
            return "red"
        return ""

    def on_close(self) -> None:
        self._emit_pending()
        execution = self._collector.execution
        self._console.print(
            f"[{_timestamp()}] Execution finished in {format_duration(execution.duration)}"
        )
        self._console.print(
            f"[{_timestamp()}] Passed: {execution.passed_scenarios}, "
            f"Failed: {execution.failed_scenarios}, Skipped: {execution.skipped_scenarios}"
        )
        if execution.undefined_scenarios:
            self._console.print(f"[{_timestamp()}] Undefined: {execution.undefined_scenarios}")
        if execution.pending_scenarios:
            self._console.print(f"[{_timestamp()}] Pending: {execution.pending_scenarios}")
