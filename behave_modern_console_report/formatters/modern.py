"""Modern Playwright-like formatter."""

from __future__ import annotations

from rich.text import Text

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import (
    feature_header,
    failures_block,
    scenario_line,
    step_line,
    summary_block,
)


class ModernFormatter(BaseFormatter):
    """Playwright-like formatter with clean output and progress at the end."""

    name = "modern"
    description = "Playwright-like console report with feature grouping"

    def __init__(self, stream, config) -> None:
        super().__init__(stream, config)
        self._printed_features: set[int] = set()
        self._printed_scenarios: set[int] = set()
        self._printed_header = False

    def _print_header(self) -> None:
        header = Text.assemble(
            ("\n🚀 Behave Modern Console Report\n", "bold"),
            ("Running scenarios...\n", ""),
        )
        self._console.print(header)

    def _print(self, text: Text) -> None:
        if not self._printed_header:
            self._printed_header = True
            self._print_header()
        self._console.print(text)

    def on_result(self) -> None:
        """Print newly completed scenarios and steps as they finish."""
        cfg = self.formatter_config
        for feature in self._collector.execution.features:
            if id(feature) not in self._printed_features:
                self._print(feature_header(feature))
                self._printed_features.add(id(feature))

            for scenario in feature.scenarios:
                if scenario.is_terminal and id(scenario) not in self._printed_scenarios:
                    self._print(scenario_line(scenario))
                    if cfg.show_steps:
                        for step in scenario.steps:
                            self._print(step_line(step))
                            if step.is_failed and step.error and cfg.show_traceback:
                                self._console.print(Text(f"      {step.error.message}", style="red"))
                                if step.error.traceback:
                                    for tb_line in step.error.traceback.splitlines():
                                        self._console.print(Text(f"      {tb_line}", style="red"))
                    self._printed_scenarios.add(id(scenario))

    def on_close(self) -> None:
        """Print progress bar, summary, and failures at the end."""
        cfg = self.formatter_config
        # Ensure all completed scenarios are printed before the final blocks.
        self.on_result()
        # Print any scenarios that were not emitted earlier (e.g. skipped).
        for feature in self._collector.execution.features:
            if id(feature) not in self._printed_features:
                self._print(feature_header(feature))
                self._printed_features.add(id(feature))
            for scenario in feature.scenarios:
                if id(scenario) not in self._printed_scenarios:
                    self._print(scenario_line(scenario))
                    if cfg.show_steps:
                        for step in scenario.steps:
                            self._print(step_line(step))
                            if step.is_failed and step.error and cfg.show_traceback:
                                self._console.print(Text(f"      {step.error.message}", style="red"))
                                if step.error.traceback:
                                    for tb_line in step.error.traceback.splitlines():
                                        self._console.print(Text(f"      {tb_line}", style="red"))
                    self._printed_scenarios.add(id(scenario))
        self._console.print(summary_block(self._collector.execution))
        if cfg.show_traceback:
            failures = failures_block(self._collector.execution)
            if failures:
                self._console.print(failures)
