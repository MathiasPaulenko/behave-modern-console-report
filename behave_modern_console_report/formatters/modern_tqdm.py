"""Live-updating modern formatter using tqdm for the progress bar."""

from __future__ import annotations

from typing import Any

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


class ModernTqdmFormatter(BaseFormatter):
    """Live-updating modern report using tqdm for broad terminal support."""

    name = "modern-tqdm"
    description = "Live-updating modern report with tqdm progress bar"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._printed_features: set[int] = set()
        self._printed_scenarios: set[int] = set()
        self._pbar: tqdm | None = None
        colorama.init()
        self._print_header()

    def _print_header(self) -> None:
        if self.formatter_config.colors:
            self._stream.write(
                f"{Style.BRIGHT}\n🚀 Behave Modern Console Report\n"
                f"{Style.RESET_ALL}Running scenarios...\n\n"
            )
        else:
            self._stream.write("\n🚀 Behave Modern Console Report\nRunning scenarios...\n\n")
        self._stream.flush()

    def _scenario_icon(self, status: str) -> str:
        return _STATUS_ICON.get(status.lower(), " ")

    def _status_color(self, status: str) -> str:
        return _STATUS_COLOR.get(status.lower(), "") if self.formatter_config.colors else ""

    def _color(self, text: str, color: str) -> str:
        if not self.formatter_config.colors or not color:
            return text
        return f"{color}{text}{Style.RESET_ALL}"

    def _print_scenarios(self) -> None:
        """Print newly completed scenarios above the progress bar."""
        cfg = self.formatter_config
        for feature in self._collector.execution.features:
            if id(feature) not in self._printed_features:
                tqdm.write(f"\nFeature: {feature.name}", file=self._stream)
                self._printed_features.add(id(feature))
            for scenario in feature.scenarios:
                if scenario.is_terminal and id(scenario) not in self._printed_scenarios:
                    status = scenario.status.name.lower()
                    icon = self._color(self._scenario_icon(status), self._status_color(status))
                    duration = f"({format_duration(scenario.duration)})" if scenario.duration else ""
                    colored_duration = self._color(duration, Style.DIM) if duration else ""
                    tqdm.write(f"  {icon} {scenario.name}  {colored_duration}", file=self._stream)
                    if cfg.show_steps:
                        for step in scenario.steps:
                            step_status = step.status.name.lower()
                            step_icon = self._color(self._scenario_icon(step_status), self._status_color(step_status))
                            step_duration = f"({format_duration(step.duration)})" if step.duration else ""
                            colored_step_duration = self._color(step_duration, Style.DIM) if step_duration else ""
                            keyword = f"{step.keyword} " if step.keyword else ""
                            tqdm.write(
                                f"    {step_icon} {keyword}{step.name}  {colored_step_duration}",
                                file=self._stream,
                            )
                    self._printed_scenarios.add(id(scenario))

    def on_result(self) -> None:
        """Update progress bar and print completed scenarios."""
        execution = self._collector.execution
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

        self._print_scenarios()
        if self._pbar.total != execution.total_scenarios:
            self._pbar.total = execution.total_scenarios
            self._pbar.refresh()
        completed = execution.completed_scenarios
        if self._pbar.n < completed:
            self._pbar.update(completed - self._pbar.n)

    def on_close(self) -> None:
        """Print final output and close the progress bar."""
        execution = self._collector.execution
        self._print_scenarios()
        if self._pbar is not None:
            tqdm.write("", file=self._stream)
            if self._pbar.total != execution.total_scenarios:
                self._pbar.total = execution.total_scenarios
                self._pbar.refresh()
            completed = execution.completed_scenarios
            if self._pbar.n < completed:
                self._pbar.update(completed - self._pbar.n)
            self._pbar.close()

        colorama.deinit()

        tqdm.write("", file=self._stream)
        tqdm.write("RESULTS", file=self._stream)
        tqdm.write(f"  {self._color('Passed', Fore.GREEN)}   {execution.passed_scenarios}", file=self._stream)
        tqdm.write(f"  {self._color('Failed', Fore.RED)}   {execution.failed_scenarios}", file=self._stream)
        tqdm.write(f"  {self._color('Skipped', Fore.YELLOW)}  {execution.skipped_scenarios}", file=self._stream)
        tqdm.write(f"  {self._color('⏱ Duration', Style.DIM)} {format_duration(execution.duration)}", file=self._stream)
