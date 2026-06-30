"""Plain log-style formatter."""

from __future__ import annotations

import datetime

from rich.text import Text

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import status_text
from behave_modern_console_report.utils import format_duration


def _timestamp() -> str:
    """Return an ISO-like timestamp for log lines."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class LogFormatter(BaseFormatter):
    """Formatter that prints every completed event as a timestamped log line."""

    name = "log"
    description = "Timestamped log output for every completed feature/scenario/step"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._printed_scenarios: set[int] = set()
        self._printed_steps: set[int] = set()

    def feature(self, feature) -> None:
        super().feature(feature)
        self._console.print(f"[{_timestamp()}] Feature: {feature.name}")

    def on_result(self) -> None:
        cfg = self.formatter_config
        for feature in self._collector.execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal and id(scenario) not in self._printed_scenarios:
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
                            if id(step) not in self._printed_steps:
                                self._printed_steps.add(id(step))
                                step_line = Text(f"[{_timestamp()}]   ")
                                step_line.append(
                                    f"[{step.status.name.upper()}]",
                                    style=self._status_style(step.status.name),
                                )
                                step_line.append(
                                    f" Step {status_text(step.status)}: {step.keyword} {step.name} "
                                    f"({format_duration(step.duration)})"
                                )
                                self._console.print(step_line)
                                if step.is_failed and step.error and cfg.show_traceback:
                                    error_line = Text(f"[{_timestamp()}]     ")
                                    error_line.append("ERROR:", style="red")
                                    error_line.append(f" {step.error.message}")
                                    self._console.print(error_line)

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
        execution = self._collector.execution
        self._console.print(f"[{_timestamp()}] Execution finished in {format_duration(execution.duration)}")
        self._console.print(
            f"[{_timestamp()}] Passed: {execution.passed_scenarios}, "
            f"Failed: {execution.failed_scenarios}, Skipped: {execution.skipped_scenarios}"
        )
