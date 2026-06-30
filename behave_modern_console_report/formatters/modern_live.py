"""Live-updating version of the modern formatter."""

from __future__ import annotations

from rich.console import Console
from rich.live import Live

from behave_modern_console_report.formatters.modern import ModernFormatter
from behave_modern_console_report.render import (
    failures_block,
    progress_bar,
    summary_block,
)


class ModernLiveFormatter(ModernFormatter):
    """Modern formatter that updates the same screen area in real time."""

    name = "modern-live"
    description = "Live-updating modern console report (requires a modern terminal)"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._console = Console(file=self._stream, color_system="auto" if self.formatter_config.colors else None)
        self._live = Live(console=self._console, auto_refresh=True, refresh_per_second=2, screen=False)
        self._live.start(refresh=True)

    def _print(self, text: str) -> None:
        """Live mode prints through the Live object instead of the stream."""
        pass  # All rendering is handled in _render_full

    def _print_header(self) -> None:
        pass

    def _render_full(self, is_final: bool = False) -> str:
        """Render the entire screen content."""
        cfg = self.formatter_config
        lines = ["🚀 Behave Modern Console Report", f"Running {self._collector.execution.total_scenarios} scenarios..."]

        for feature in self._collector.execution.features:
            lines.append(f"\nFeature: {feature.name}")
            for scenario in feature.scenarios:
                from behave_modern_console_report.render import scenario_line, step_line
                lines.append(scenario_line(scenario, colors=cfg.colors))
                if cfg.show_steps:
                    for step in scenario.steps:
                        lines.append(step_line(step, colors=cfg.colors))

        if cfg.show_progress:
            lines.append(progress_bar(self._collector.execution, colors=cfg.colors))
        lines.append(summary_block(self._collector.execution, colors=cfg.colors))
        if is_final and cfg.show_traceback:
            failures = failures_block(self._collector.execution, colors=cfg.colors)
            if failures:
                lines.append(failures)
        return "\n".join(lines)

    def on_result(self) -> None:
        """Refresh the live display."""
        self._live.update(self._render_full())

    def on_close(self) -> None:
        """Render the final state and stop the live display."""
        self._live.update(self._render_full(is_final=True))
        self._live.stop()
