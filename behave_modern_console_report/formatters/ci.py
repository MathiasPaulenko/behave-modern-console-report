"""CI-friendly formatter."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rich.text import Text

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import failures_block, progress_bar, summary_block
from behave_modern_console_report.utils import format_duration

if TYPE_CHECKING:
    from behave_modern_console_report.models import Feature, Scenario


class CIFormatter(BaseFormatter):
    """CI-friendly formatter with colored status tags and final failure summary."""

    name = "ci"
    description = "Plain text output suitable for CI logs"

    def __init__(self, stream: Any, config: Any) -> None:
        super().__init__(stream, config)
        self._printed_scenarios: set[int] = set()
        self._printed_steps: set[int] = set()

    def _emit_scenario(self, feature: Feature, scenario: Scenario) -> None:
        """Print a scenario line and its steps (first time only)."""
        self._printed_scenarios.add(id(scenario))
        line = Text()
        line.append(
            f"[{scenario.status.name.upper()}]",
            style=self._status_style(scenario.status.name),
        )
        line.append(f" {feature.name} / {scenario.name} ({format_duration(scenario.duration)})")
        self._console.print(line)
        if self.formatter_config.show_steps:
            for step in scenario.steps:
                if id(step) in self._printed_steps:
                    continue
                self._printed_steps.add(id(step))
                step_text = Text()
                step_text.append(
                    f"  [{step.status.name.upper()}]",
                    style=self._status_style(step.status.name),
                )
                step_text.append(f" {step.keyword} {step.name} ({format_duration(step.duration)})")
                self._console.print(step_text)

    def _emit_pending(self) -> None:
        """Print all terminal scenarios that have not been emitted yet."""
        for feature in self._collector.execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal and id(scenario) not in self._printed_scenarios:
                    self._emit_scenario(feature, scenario)

    def on_result(self) -> None:
        """Print a colored line for each newly completed scenario."""
        self._emit_pending()

    def on_close(self) -> None:
        """Print a final progress bar, summary, and failure details."""
        cfg = self.formatter_config
        self._emit_pending()
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
