"""Single-line live progress formatter."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.utils import format_duration

if TYPE_CHECKING:
    from behave_modern_console_report.models import Scenario

_ANSI_GREEN = "\033[32m"
_ANSI_DIM = "\033[2m"
_ANSI_RESET = "\033[0m"


class ProgressFormatter(BaseFormatter):
    """Single-line live progress bar that updates in place."""

    name = "progress"
    description = "Single-line live progress bar that updates in place"

    def __init__(self, stream: Any, config: Any) -> None:
        super().__init__(stream, config)
        self._actual_stream = self._stream
        self._last_completed = -1
        self._is_tty = hasattr(self._actual_stream, "isatty") and self._actual_stream.isatty()

    def _use_colors(self) -> bool:
        """ANSI colors only make sense on a real terminal, never on files."""
        return self.formatter_config.colors and self._is_tty

    def _running_scenario(self) -> Scenario | None:
        for feature in self._collector.execution.features:
            for scenario in feature.scenarios:
                if not scenario.is_terminal:
                    return scenario
        return None

    def _render_line(self) -> str:
        execution = self._collector.execution
        total = execution.total_scenarios
        completed = execution.completed_scenarios
        if total == 0:
            text = "Running scenarios..."
            return self._dim(text)
        percent = int(completed / total * 100)
        width = 20
        filled = int(width * completed / total)
        bar = "█" * filled + "░" * (width - filled)
        running = self._running_scenario()
        running_text = running.name if running else "done"
        if self._use_colors():
            bar = f"{_ANSI_GREEN}{bar}{_ANSI_RESET}"
            running_text = f"{_ANSI_DIM}{running_text}{_ANSI_RESET}"
        return f"{bar} {percent}% {completed}/{total} - {running_text}"

    def _dim(self, text: str) -> str:
        if not self._use_colors():
            return text
        return f"{_ANSI_DIM}{text}{_ANSI_RESET}"

    def _print_line(self) -> None:
        if self._is_tty:
            self._actual_stream.write("\r\033[K")
            self._actual_stream.write(self._render_line())
        else:
            self._actual_stream.write(self._render_line() + "\n")
        self._actual_stream.flush()

    def on_result(self) -> None:
        """Update the progress bar only when a scenario completes."""
        completed = self._collector.execution.completed_scenarios
        if completed != self._last_completed:
            self._last_completed = completed
            self._print_line()

    def on_close(self) -> None:
        """Finalize the line and print the results."""
        self._print_line()
        if self._is_tty:
            self._actual_stream.write("\n")
            self._actual_stream.flush()
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
