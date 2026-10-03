"""Minimal formatter."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.utils import format_duration

if TYPE_CHECKING:
    from behave_modern_console_report.models import Scenario


class MinimalFormatter(BaseFormatter):
    """Minimal formatter that shows only scenarios and a final summary."""

    name = "minimal"
    description = "Minimal plain text output with only scenarios and summary"

    def __init__(self, stream: Any, config: Any) -> None:
        super().__init__(stream, config)
        self._printed_scenarios: set[int] = set()

    def _emit_scenario(self, scenario: Scenario) -> None:
        """Print a scenario line (first time only)."""
        self._printed_scenarios.add(id(scenario))
        status = scenario.status.name.upper()
        self._console.print(
            f"[{status}] {scenario.name} ({format_duration(scenario.duration)})",
            style="",
        )

    def _emit_pending(self) -> None:
        """Print all terminal scenarios that have not been emitted yet."""
        for feature in self._collector.execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal and id(scenario) not in self._printed_scenarios:
                    self._emit_scenario(scenario)

    def on_result(self) -> None:
        """Print a plain line for each newly completed scenario."""
        self._emit_pending()

    def on_close(self) -> None:
        """Print the final summary in plain text."""
        self._emit_pending()
        execution = self._collector.execution
        self._console.print("RESULTS")
        self._console.print(f"  Passed {execution.passed_scenarios}")
        self._console.print(f"  Failed {execution.failed_scenarios}")
        self._console.print(f"  Skipped {execution.skipped_scenarios}")
        if execution.undefined_scenarios:
            self._console.print(f"  Undefined {execution.undefined_scenarios}")
        if execution.pending_scenarios:
            self._console.print(f"  Pending {execution.pending_scenarios}")
        self._console.print(f"  Duration {format_duration(execution.duration)}")
