"""Experimental single-line live progress bar using prompt_toolkit output."""

from __future__ import annotations

import colorama
from colorama import Fore, Style
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.output import create_output

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.models import Scenario
from behave_modern_console_report.utils import format_duration


class ModernTestFormatter(BaseFormatter):
    """Experimental single-line live progress bar using prompt_toolkit."""

    name = "modern-test"
    description = "Experimental single-line live progress bar using prompt_toolkit"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._actual_stream = stream.open() if hasattr(stream, "open") else stream
        self._output = create_output(stdout=self._actual_stream)
        colorama.init()

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
            return self._gray(text) if self.formatter_config.colors else text
        percent = int(completed / total * 100)
        width = 20
        filled = int(width * completed / total)
        bar = "█" * filled + "░" * (width - filled)
        running = self._running_scenario()
        running_text = running.name if running else "done"
        if self.formatter_config.colors:
            bar = f"{Fore.GREEN}{bar}{Style.RESET_ALL}"
            running_text = f"{Style.DIM}{running_text}{Style.RESET_ALL}"
        return f"{bar} {percent}% {completed}/{total} - {running_text}"

    def _gray(self, text: str) -> str:
        if not self.formatter_config.colors:
            return text
        return f"{Style.DIM}{text}{Style.RESET_ALL}"

    def _print_line(self) -> None:
        line = self._render_line()
        self._actual_stream.write("\r\033[K")
        self._actual_stream.write(line)
        self._actual_stream.flush()

    def on_result(self) -> None:
        """Update the single-line live progress bar."""
        self._print_line()

    def on_close(self) -> None:
        """Finalize the line and print the results."""
        self._print_line()
        self._actual_stream.write("\n")
        execution = self._collector.execution
        print_formatted_text(HTML(
            f"<b>RESULTS</b><br/>"
            f"  <ansigreen>Passed</ansigreen>   {execution.passed_scenarios}<br/>"
            f"  <ansired>Failed</ansired>   {execution.failed_scenarios}<br/>"
            f"  <ansiyellow>Skipped</ansiyellow>  {execution.skipped_scenarios}<br/>"
            f"  <dim>⏱ Duration</dim> {format_duration(execution.duration)}"
        ), output=self._output)
