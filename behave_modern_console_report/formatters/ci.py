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

    def _print(self, text: str) -> None:
        self._stream.write(text + "\n")
        self._stream.flush()

    def on_result(self) -> None:
        """Print a plain line for each completed scenario."""
        for feature in self._collector.execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal:
                    status = scenario.status.name.upper()
                    self._print(f"[{status}] {feature.name} / {scenario.name} ({format_duration(scenario.duration)})")
                    if self.formatter_config.show_steps:
                        for step in scenario.steps:
                            step_status = step.status.name.upper()
                            self._print(f"  [{step_status}] {step.keyword} {step.name} ({format_duration(step.duration)})")

    def on_close(self) -> None:
        """Print a final progress bar and summary."""
        cfg = self.formatter_config
        if cfg.show_progress:
            self._print(progress_bar(self._collector.execution, colors=False))
        self._print(summary_block(self._collector.execution, colors=False))
