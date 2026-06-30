"""Plain log-style formatter."""

from __future__ import annotations

import datetime

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import icon, status_text
from behave_modern_console_report.utils import format_duration


def _timestamp() -> str:
    """Return an ISO-like timestamp for log lines."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class LogFormatter(BaseFormatter):
    """Formatter that prints every event as a timestamped log line."""

    name = "log"
    description = "Timestamped log output for every feature/scenario/step"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)

    def _print(self, text: str) -> None:
        self._stream.write(text + "\n")
        self._stream.flush()

    def feature(self, feature) -> None:
        super().feature(feature)
        cfg = self.formatter_config
        self._print(f"[{_timestamp()}] {icon(self._collector.execution.features[-1].status, cfg.colors)} Feature: {feature.name}")

    def scenario(self, scenario) -> None:
        super().scenario(scenario)

    def on_result(self) -> None:
        cfg = self.formatter_config
        execution = self._collector.execution
        for feature in execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal:
                    self._print(
                        f"[{_timestamp()}] {icon(scenario.status, cfg.colors)} Scenario "
                        f"{status_text(scenario.status)}: {scenario.name} ({format_duration(scenario.duration)})"
                    )
                    if cfg.show_steps:
                        for step in scenario.steps:
                            self._print(
                                f"[{_timestamp()}]   {icon(step.status, cfg.colors)} Step "
                                f"{status_text(step.status)}: {step.keyword} {step.name} ({format_duration(step.duration)})"
                            )
                            if step.is_failed and step.error and cfg.show_traceback:
                                self._print(f"[{_timestamp()}]     ERROR: {step.error.message}")

    def on_close(self) -> None:
        cfg = self.formatter_config
        execution = self._collector.execution
        self._print(f"[{_timestamp()}] Execution finished in {format_duration(execution.duration)}")
        self._print(f"[{_timestamp()}] Passed: {execution.passed_scenarios}, Failed: {execution.failed_scenarios}, Skipped: {execution.skipped_scenarios}")
