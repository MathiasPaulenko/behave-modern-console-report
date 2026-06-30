"""Progress formatter."""

from __future__ import annotations

import time

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import progress_bar, scenario_line, summary_block


class ProgressFormatter(BaseFormatter):
    """Prints a progress bar after each completed scenario."""

    name = "progress"
    description = "Prints a fresh progress bar after every scenario"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._last_progress = 0.0

    def on_result(self) -> None:
        cfg = self.formatter_config
        # Throttle progress bar updates to once per 0.5 seconds to avoid spam.
        now = time.monotonic()
        if now - self._last_progress < 0.5:
            return
        self._last_progress = now

        for feature in self._collector.execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal:
                    self._console.print(scenario_line(scenario))
        if cfg.show_progress:
            self._console.print(progress_bar(self._collector.execution))

    def on_close(self) -> None:
        cfg = self.formatter_config
        for feature in self._collector.execution.features:
            for scenario in feature.scenarios:
                if scenario.is_terminal:
                    self._console.print(scenario_line(scenario))
        if cfg.show_progress:
            self._console.print(progress_bar(self._collector.execution))
        self._console.print(summary_block(self._collector.execution))
