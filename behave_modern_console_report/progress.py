"""Progress bar rendering for the modern console formatter."""

from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style
from rich.text import Text

from behave_modern_console_report.models import Execution
from behave_modern_console_report.themes import Theme
from behave_modern_console_report.utils import estimate_remaining, format_duration


class ProgressBar:
    """Renderable progress bar with percentage and ETA."""

    def __init__(self, width: int = 24, theme: Theme | None = None) -> None:
        self.width = max(1, width)
        self.theme = theme

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield Text("Progress bar requires an Execution context")

    def render(self, execution: Execution) -> Text:
        """Render the progress bar for the current execution state."""
        percent = execution.completion_rate
        filled = int(self.width * percent)
        empty = self.width - filled
        bar = "█" * filled + "░" * empty
        percent_text = f"{int(percent * 100)}%"
        line = f"{bar}  {percent_text}"

        text = Text(line)
        if self.theme:
            fill_style = self.theme.progress_fill
            empty_style = self.theme.progress_empty
            text.stylize(fill_style, 0, filled)
            text.stylize(empty_style, filled, self.width)
        return text

    def render_with_counts(self, execution: Execution) -> Text:
        """Render the progress bar plus scenario counts and ETA."""
        bar = self.render(execution)
        counts = f"  {execution.completed_scenarios} / {execution.total_scenarios} scenarios"
        eta = ""
        if execution.start_time is not None and execution.end_time is None:
            elapsed = execution.duration
            remaining = estimate_remaining(elapsed, execution.completed_scenarios, execution.total_scenarios)
            if remaining is not None:
                eta = f"  ETA {format_duration(remaining)}"
        return Text.assemble(bar, Text(counts), Text(eta))


class BarRenderable:
    """Simple console-renderable bar segment for low-overhead use."""

    def __init__(self, width: int, percent: float, fill_style: Style, empty_style: Style):
        self.width = width
        self.percent = max(0.0, min(1.0, percent))
        self.fill_style = fill_style
        self.empty_style = empty_style

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        filled = int(self.width * self.percent)
        for index in range(self.width):
            style = self.fill_style if index < filled else self.empty_style
            yield Segment("█", style)

    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        return Measurement(self.width, self.width)
