"""CI-friendly formatter."""

from __future__ import annotations

from rich.text import Text

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import failures_block, progress_bar, summary_block
from behave_modern_console_report.utils import format_duration


class CIFormatter(BaseFormatter):
    """CI-friendly formatter with colored status tags and final failure summary."""

    name = "ci"
    description = "Plain text output suitable for CI logs"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._printed_scenarios: set[int] = set()
        self._printed_steps: set[int] = set()

    def on_result(self) -> None:
        """Print a colored line for each newly completed scenario."""
        for feature in self._collector.execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal and id(scenario) not in self._printed_scenarios:
                    self._printed_scenarios.add(id(scenario))
                    line = Text()
                    line.append(
                        f"[{scenario.status.name.upper()}]",
                        style=self._status_style(scenario.status.name),
                    )
                    line.append(
                        f" {feature.name} / {scenario.name} ({format_duration(scenario.duration)})"
                    )
                    self._console.print(line)
                    if self.formatter_config.show_steps:
                        for step in scenario.steps:
                            if id(step) not in self._printed_steps:
                                self._printed_steps.add(id(step))
                                step_line = Text()
                                step_line.append(
                                    f"  [{step.status.name.upper()}]",
                                    style=self._status_style(step.status.name),
                                )
                                step_line.append(
                                    f" {step.keyword} {step.name} ({format_duration(step.duration)})"
                                )
                                self._console.print(step_line)

    def on_close(self) -> None:
        """Print a final progress bar, summary, and failure details."""
        cfg = self.formatter_config
        if cfg.show_progress:
            self._console.print(progress_bar(self._collector.execution))
        self._console.print(summary_block(self._collector.execution))
        if cfg.show_traceback:
            failures = failures_block(self._collector.execution)
            if failures:
                self._console.print(failures)

    def _status_style(self, status: str) -> str:
        status = status.lower()
        if status == "passed":
            return "green"
        if status == "skipped":
            return "blue"
        if status == "failed":
            return "red"
        return ""
