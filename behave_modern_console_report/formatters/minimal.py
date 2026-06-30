"""Minimal formatter."""

from __future__ import annotations

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import (
    STATUS_ICON,
    STATUS_STYLE,
    failures_block,
    summary_block,
)
from behave_modern_console_report.utils import format_duration


class MinimalFormatter(BaseFormatter):
    """Minimal formatter that shows scenarios as they complete and a final summary."""

    name = "minimal"
    description = "Minimal output with executed scenarios and final summary"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._printed_scenarios: set[int] = set()

    def on_result(self) -> None:
        """Print a compact line for each newly completed scenario."""
        for feature in self._collector.execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal and id(scenario) not in self._printed_scenarios:
                    self._printed_scenarios.add(id(scenario))
                    icon = STATUS_ICON.get(scenario.status, " ")
                    style = STATUS_STYLE.get(scenario.status, "")
                    self._console.print(
                        f"{icon} {scenario.name} ({format_duration(scenario.duration)})",
                        style=style,
                    )
                    if self.formatter_config.show_steps:
                        for step in scenario.steps:
                            step_icon = STATUS_ICON.get(step.status, " ")
                            step_style = STATUS_STYLE.get(step.status, "")
                            self._console.print(
                                f"    {step_icon} {step.keyword} {step.name} ({format_duration(step.duration)})",
                                style=step_style,
                            )

    def on_close(self) -> None:
        """Print the final summary and failure details."""
        self._console.print(summary_block(self._collector.execution))
        if self.formatter_config.show_traceback:
            failures = failures_block(self._collector.execution)
            if failures:
                self._console.print(failures)
