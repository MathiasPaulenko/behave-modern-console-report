"""Experimental formatter using blessed for live cursor control and status updates."""

from __future__ import annotations

from blessed import Terminal

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.utils import format_duration


_STATUS_ICON = {
    "passed": "✓",
    "failed": "✗",
    "skipped": "⏭",
    "running": "◌",
    "untested": " ",
}

_STATUS_COLOR = {
    "passed": 2,   # green
    "failed": 1,   # red
    "skipped": 3,  # yellow
    "running": 8,  # bright black / gray
    "untested": 8,
}


class ModernTestFormatter(BaseFormatter):
    """Experimental live report using blessed terminal control."""

    name = "modern-test"
    description = "Experimental formatter using blessed for live status updates"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._term = Terminal(stream=self._stream)
        self._line_count = 0

    def _icon(self, status: str) -> str:
        return _STATUS_ICON.get(status.lower(), " ")

    def _status_color(self, status: str) -> int:
        return _STATUS_COLOR.get(status.lower(), 8)

    def _colored(self, text: str, color_index: int) -> str:
        if not self.formatter_config.colors:
            return text
        return f"{self._term.color(color_index)}{text}{self._term.normal}"

    def _render_lines(self) -> list[str]:
        """Render all scenario/step lines for the current execution state."""
        cfg = self.formatter_config
        lines = []
        lines.append("🚀 Behave Modern Console Report")
        lines.append("Running scenarios...")
        for feature in self._collector.execution.features:
            lines.append(f"Feature: {feature.name}")
            for scenario in feature.scenarios:
                status = scenario.status.name.lower()
                icon = self._colored(self._icon(status), self._status_color(status))
                duration = f"({format_duration(scenario.duration)})" if scenario.duration else ""
                colored_duration = self._colored(duration, 8) if duration else ""
                lines.append(f"  {icon} {scenario.name}  {colored_duration}")
                if cfg.show_steps:
                    for step in scenario.steps:
                        step_status = step.status.name.lower()
                        step_icon = self._colored(self._icon(step_status), self._status_color(step_status))
                        step_duration = f"({format_duration(step.duration)})" if step.duration else ""
                        colored_step_duration = self._colored(step_duration, 8) if step_duration else ""
                        keyword = f"{step.keyword} " if step.keyword else ""
                        lines.append(f"    {step_icon} {keyword}{step.name}  {colored_step_duration}")
                        if step.is_failed and step.error and cfg.show_traceback:
                            lines.append(self._colored(f"      {step.error.message}", 1))
                            if step.error.traceback:
                                for tb_line in step.error.traceback.splitlines():
                                    lines.append(self._colored(f"      {tb_line}", 1))
        execution = self._collector.execution
        if execution.total_scenarios > 0:
            width = 28
            filled = int(width * execution.completion_rate)
            bar = "█" * filled + "░" * (width - filled)
            percent = int(execution.completion_rate * 100)
            lines.append("")
            lines.append(f"{bar}  {percent}%  {execution.completed_scenarios} / {execution.total_scenarios} scenarios")
        return lines

    def _print_lines(self, lines: list[str]) -> None:
        """Clear the previous render and print the new one in place."""
        new_count = len(lines)
        clear_count = max(self._line_count, new_count)
        if clear_count > 0:
            self._stream.write(self._term.move_up(clear_count))
            for _ in range(clear_count):
                self._stream.write(self._term.clear_eol)
                self._stream.write(self._term.move_down())
            self._stream.write(self._term.move_up(clear_count))
        for line in lines:
            self._stream.write(line + "\n")
        self._line_count = new_count
        self._stream.flush()

    def on_result(self) -> None:
        """Refresh the live display."""
        lines = self._render_lines()
        self._print_lines(lines)

    def on_close(self) -> None:
        """Print the final state and results."""
        lines = self._render_lines()
        self._print_lines(lines)
        execution = self._collector.execution
        self._stream.write("\nRESULTS\n")
        self._stream.write(f"  {self._colored('Passed', 2)}   {execution.passed_scenarios}\n")
        self._stream.write(f"  {self._colored('Failed', 1)}   {execution.failed_scenarios}\n")
        self._stream.write(f"  {self._colored('Skipped', 3)}  {execution.skipped_scenarios}\n")
        self._stream.write(f"  {self._colored('⏱ Duration', 8)} {format_duration(execution.duration)}\n")
        self._stream.flush()
