"""Minimal formatter."""

from __future__ import annotations

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import summary_block


class MinimalFormatter(BaseFormatter):
    """Minimal formatter that only shows the final summary."""

    name = "minimal"
    description = "Only the final summary, no scenario details"

    def on_result(self) -> None:
        """No intermediate output."""
        pass

    def on_close(self) -> None:
        """Print the final summary."""
        self._console.print(summary_block(self._collector.execution))
