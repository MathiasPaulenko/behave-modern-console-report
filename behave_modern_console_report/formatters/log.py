"""Plain log-style formatter."""

from __future__ import annotations

import datetime

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import status_text
from behave_modern_console_report.utils import format_duration


def _timestamp() -> str:
    """Return an ISO-like timestamp for log lines."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class LogFormatter(BaseFormatter):
    """Formatter that prints every event as a timestamped log line."""

    name = "log"
    description = "Timestamped log output for every feature/scenario/step"

    def feature(self, feature) -> None:
        super().feature(feature)
        cfg = self.formatter_config
        icon = "✓" if feature.status.name in {"passed", "skipped"} else "✗"
        self._console.print(f"[{_timestamp()}] {icon} Feature: {feature.name}")

    def on_result(self) -> None:
        cfg = self.formatter_config
        execution = self._collector.execution
        for feature in execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal:
                    self._console.print(
                        f"[{_timestamp()}] [{scenario.status.name.upper()}] Scenario "
                        f"{status_text(scenario.status)}: {scenario.name} ({format_duration(scenario.duration)})"
                    )
                    if cfg.show_steps:
                        for step in scenario.steps:
                            self._console.print(
                                f"[{_timestamp()}]   [{step.status.name.upper()}] Step "
                                f"{status_text(step.status)}: {step.keyword} {step.name} ({format_duration(step.duration)})"
                            )
                            if step.is_failed and step.error and cfg.show_traceback:
                                self._console.print(f"[{_timestamp()}]     ERROR: {step.error.message}")

    def on_close(self) -> None:
        execution = self._collector.execution
        self._console.print(f"[{_timestamp()}] Execution finished in {format_duration(execution.duration)}")
        self._console.print(
            f"[{_timestamp()}] Passed: {execution.passed_scenarios}, "
            f"Failed: {execution.failed_scenarios}, Skipped: {execution.skipped_scenarios}"
        )
