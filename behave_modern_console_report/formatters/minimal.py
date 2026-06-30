"""Minimal formatter."""

from __future__ import annotations

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import summary_block


class MinimalFormatter(BaseFormatter):
    """Minimal formatter that only shows the final summary."""

    name = "minimal"
    description = "Only the final summary, no scenario details"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)

    def on_result(self) -> None:
        """No intermediate output."""
        pass

    def on_close(self) -> None:
        """Print the final summary."""
        self._stream.write(summary_block(self._collector.execution, colors=self.formatter_config.colors) + "\n")
        self._stream.flush()
