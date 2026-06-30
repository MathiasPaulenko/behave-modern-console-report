"""Minimal formatter."""

from __future__ import annotations

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.utils import format_duration


class MinimalFormatter(BaseFormatter):
    """Minimal formatter that shows only scenarios and a final summary."""

    name = "minimal"
    description = "Minimal plain text output with only scenarios and summary"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._printed_scenarios: set[int] = set()

    def on_result(self) -> None:
        """Print a plain line for each newly completed scenario."""
        for feature in self._collector.execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal and id(scenario) not in self._printed_scenarios:
                    self._printed_scenarios.add(id(scenario))
                    status = scenario.status.name.upper()
                    self._console.print(
                        f"[{status}] {scenario.name} ({format_duration(scenario.duration)})",
                        style="",
                    )

    def on_close(self) -> None:
        """Print the final summary in plain text."""
        execution = self._collector.execution
        self._console.print("RESULTS")
        self._console.print(f"  Passed {execution.passed_scenarios}")
        self._console.print(f"  Failed {execution.failed_scenarios}")
        self._console.print(f"  Skipped {execution.skipped_scenarios}")
        self._console.print(f"  Duration {format_duration(execution.duration)}")
