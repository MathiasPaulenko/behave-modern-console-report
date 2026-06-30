"""Live-updating version of the modern formatter."""

from __future__ import annotations

from rich.console import Console
from rich.live import Live
from rich.text import Text

from behave_modern_console_report.formatters.modern import ModernFormatter
from behave_modern_console_report.render import (
    failures_block,
    feature_header,
    progress_bar,
    scenario_line,
    step_line,
    summary_block,
)


class ModernLiveFormatter(ModernFormatter):
    """Modern formatter that updates the same screen area in real time."""

    name = "modern-live"
    description = "Live-updating modern console report (requires a modern terminal)"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._console = Console(
            file=self._stream,
            color_system="auto" if self.formatter_config.colors else None,
        )
        self._live = Live(
            console=self._console,
            auto_refresh=True,
            refresh_per_second=2,
            screen=False,
            vertical_overflow="visible",
        )
        self._live.start(refresh=True)

    def _print(self, text: Text) -> None:
        """Live mode prints through the Live object instead of the stream."""
        pass  # All rendering is handled in _render_full

    def _print_header(self) -> None:
        pass

    def _render_full(self, is_final: bool = False) -> Text:
        """Render the entire screen content as a single Text object."""
        cfg = self.formatter_config
        output = Text()
        output.append("🚀 Behave Modern Console Report\n", style="bold")
        output.append(f"Running {self._collector.execution.total_scenarios} scenarios...\n")

        for feature in self._collector.execution.features:
            output.append_text(feature_header(feature))
            output.append("\n")
            for scenario in feature.scenarios:
                output.append_text(scenario_line(scenario))
                output.append("\n")
                if cfg.show_steps:
                    for step in scenario.steps:
                        output.append_text(step_line(step))
                        output.append("\n")

        if cfg.show_progress:
            output.append("\n")
            output.append_text(progress_bar(self._collector.execution))
            output.append("\n")
        if is_final:
            output.append_text(summary_block(self._collector.execution))
            if cfg.show_traceback:
                failures = failures_block(self._collector.execution)
                if failures:
                    output.append_text(failures)
        return output

    def on_result(self) -> None:
        """Refresh the live display."""
        self._live.update(self._render_full())

    def on_close(self) -> None:
        """Render the final state and stop the live display."""
        self._live.update(self._render_full(is_final=True))
        self._live.stop()
