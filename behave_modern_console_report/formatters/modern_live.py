"""Live-updating modern formatter using Rich Live for real-time status colors."""

from __future__ import annotations

from rich.live import Live
from rich.text import Text

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import (
    feature_header,
    failures_block,
    progress_bar,
    scenario_line,
    step_line,
    summary_block,
)


class ModernLiveFormatter(BaseFormatter):
    """Live-updating modern report with real-time status colors."""

    name = "modern-live"
    description = "Live-updating modern report with real-time status colors"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._live = Live(
            console=self._console,
            auto_refresh=True,
            refresh_per_second=2,
            screen=False,
            vertical_overflow="visible",
        )
        self._live.start(refresh=True)
        self._live.update(self._render())

    def _render(self, is_final: bool = False) -> Text:
        """Render the full report. Running scenarios/steps are dim; completed are colored."""
        cfg = self.formatter_config
        lines = Text()
        lines.append("\n🚀 Behave Modern Console Report\n", style="bold")
        lines.append("Running scenarios...\n")
        for feature in self._collector.execution.features:
            lines.append_text(feature_header(feature))
            for scenario in feature.scenarios:
                lines.append_text(scenario_line(scenario))
                if cfg.show_steps:
                    for step in scenario.steps:
                        lines.append_text(step_line(step))
                        if step.is_failed and step.error and cfg.show_traceback:
                            lines.append(f"      {step.error.message}\n", style="red")
                            if step.error.traceback:
                                for tb_line in step.error.traceback.splitlines():
                                    lines.append(f"      {tb_line}\n", style="red")
        if cfg.show_progress or is_final:
            lines.append(Text(""))
            lines.append_text(progress_bar(self._collector.execution))
        if is_final:
            lines.append_text(summary_block(self._collector.execution))
            if cfg.show_traceback:
                failures = failures_block(self._collector.execution)
                if failures:
                    lines.append_text(failures)
        return lines

    def on_result(self) -> None:
        """Refresh the live display with the current execution state."""
        self._live.update(self._render())

    def on_close(self) -> None:
        """Show the final report and stop the live display."""
        self._live.update(self._render(is_final=True))
        self._live.stop()
