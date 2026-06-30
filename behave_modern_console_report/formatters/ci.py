"""CI-friendly formatter."""

from __future__ import annotations

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import progress_bar, summary_block
from behave_modern_console_report.utils import format_duration


class CIFormatter(BaseFormatter):
    """Minimal CI-friendly formatter with no colors and a final summary."""

    name = "ci"
    description = "Plain text output suitable for CI logs"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._printed_scenarios: set[int] = set()
        self._printed_steps: set[int] = set()

    def on_result(self) -> None:
        """Print a plain line for each newly completed scenario."""
        for feature in self._collector.execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal and id(scenario) not in self._printed_scenarios:
                    self._printed_scenarios.add(id(scenario))
                    status = scenario.status.name.upper()
                    self._console.print(
                        f"[{status}] {feature.name} / {scenario.name} ({format_duration(scenario.duration)})"
                    )
                    if self.formatter_config.show_steps:
                        for step in scenario.steps:
                            if id(step) not in self._printed_steps:
                                self._printed_steps.add(id(step))
                                step_status = step.status.name.upper()
                                self._console.print(
                                    f"  [{step_status}] {step.keyword} {step.name} ({format_duration(step.duration)})"
                                )

    def on_close(self) -> None:
        """Print a final progress bar and summary."""
        cfg = self.formatter_config
        if cfg.show_progress:
            self._console.print(progress_bar(self._collector.execution))
        self._console.print(summary_block(self._collector.execution))
