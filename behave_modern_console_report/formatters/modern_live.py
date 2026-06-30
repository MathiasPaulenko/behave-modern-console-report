"""Live-updating modern formatter using tqdm and ANSI escape codes for status updates."""

from __future__ import annotations

import colorama
from colorama import Fore, Style
from tqdm import tqdm

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.utils import format_duration


_STATUS_ICON = {
    "passed": "✓",
    "failed": "✗",
    "skipped": "⏭",
    "undefined": "?",
    "pending": "P",
    "running": "◌",
    "untested": " ",
}

_STATUS_COLOR = {
    "passed": Fore.GREEN,
    "failed": Fore.RED,
    "skipped": Fore.YELLOW,
    "undefined": Fore.MAGENTA,
    "pending": Fore.YELLOW,
    "running": Style.DIM,
    "untested": Style.DIM,
}


class ModernLiveFormatter(BaseFormatter):
    """Live-updating modern report with tqdm progress bar and ANSI status updates."""

    name = "modern-live"
    description = "Live-updating modern report with tqdm progress bar and ANSI status updates"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._pbar: tqdm | None = None
        self._line_count = 0
        colorama.init()

    def _scenario_icon(self, status: str) -> str:
        return _STATUS_ICON.get(status.lower(), " ")

    def _status_color(self, status: str) -> str:
        return _STATUS_COLOR.get(status.lower(), "") if self.formatter_config.colors else ""

    def _color(self, text: str, color: str) -> str:
        if not self.formatter_config.colors or not color:
            return text
        return f"{color}{text}{Style.RESET_ALL}"

    def _render_lines(self) -> list[str]:
        """Render all scenario/step lines for the current execution state."""
        cfg = self.formatter_config
        lines = []
        lines.append("\n🚀 Behave Modern Console Report")
        lines.append("Running scenarios...")
        for feature in self._collector.execution.features:
            lines.append(f"Feature: {feature.name}")
            for scenario in feature.scenarios:
                status = scenario.status.name.lower()
                icon = self._color(self._scenario_icon(status), self._status_color(status))
                duration = f"({format_duration(scenario.duration)})" if scenario.duration else ""
                colored_duration = self._color(duration, Style.DIM) if duration else ""
                lines.append(f"  {icon} {scenario.name}  {colored_duration}")
                if cfg.show_steps:
                    for step in scenario.steps:
                        step_status = step.status.name.lower()
                        step_icon = self._color(self._scenario_icon(step_status), self._status_color(step_status))
                        step_duration = f"({format_duration(step.duration)})" if step.duration else ""
                        colored_step_duration = self._color(step_duration, Style.DIM) if step_duration else ""
                        keyword = f"{step.keyword} " if step.keyword else ""
                        lines.append(f"    {step_icon} {keyword}{step.name}  {colored_step_duration}")
                        if step.is_failed and step.error and cfg.show_traceback:
                            lines.append(f"      {self._color(step.error.message, Fore.RED)}")
                            if step.error.traceback:
                                for tb_line in step.error.traceback.splitlines():
                                    lines.append(f"      {self._color(tb_line, Fore.RED)}")
        return lines

    def _print_lines(self, lines: list[str]) -> None:
        """Clear the previous scenario area (and bar if present) and print the new lines."""
        new_count = len(lines)
        clear_count = max(self._line_count, new_count) + (1 if self._pbar is not None else 0)
        if clear_count > 0:
            # Move up clear_count lines, clear each one, then return to the first line.
            self._stream.write(f"\033[{clear_count}A")
            for _ in range(clear_count):
                self._stream.write("\033[K\033[B")
            self._stream.write(f"\033[{clear_count}A")
        for line in lines:
            self._stream.write(line + "\n")
        self._line_count = new_count
        self._stream.flush()

    def on_result(self) -> None:
        """Update the scenario area and the progress bar."""
        execution = self._collector.execution
        lines = self._render_lines()
        self._print_lines(lines)

        if self._pbar is None:
            self._pbar = tqdm(
                total=execution.total_scenarios,
                desc="Scenarios",
                unit="scen",
                file=self._stream,
                dynamic_ncols=True,
                colour="green" if self.formatter_config.colors else None,
                disable=execution.total_scenarios == 0,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} scenarios [{elapsed}]",
            )

        if self._pbar.total != execution.total_scenarios:
            self._pbar.total = execution.total_scenarios
            self._pbar.refresh()
        completed = execution.completed_scenarios
        if self._pbar.n < completed:
            self._pbar.update(completed - self._pbar.n)

    def on_close(self) -> None:
        """Print the final state and close the progress bar."""
        execution = self._collector.execution
        lines = self._render_lines()
        self._print_lines(lines)

        if self._pbar is not None:
            if self._pbar.total != execution.total_scenarios:
                self._pbar.total = execution.total_scenarios
                self._pbar.refresh()
            completed = execution.completed_scenarios
            if self._pbar.n < completed:
                self._pbar.update(completed - self._pbar.n)
            self._pbar.close()

        colorama.deinit()

        self._stream.write("\nRESULTS\n")
        self._stream.write(f"  {self._color('Passed', Fore.GREEN)}   {execution.passed_scenarios}\n")
        self._stream.write(f"  {self._color('Failed', Fore.RED)}   {execution.failed_scenarios}\n")
        self._stream.write(f"  {self._color('Skipped', Fore.YELLOW)}  {execution.skipped_scenarios}\n")
        self._stream.write(f"  {self._color('⏱ Duration', Style.DIM)} {format_duration(execution.duration)}\n")
        self._stream.flush()
