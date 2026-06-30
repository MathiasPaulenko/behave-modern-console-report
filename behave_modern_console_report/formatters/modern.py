"""Modern Playwright-like formatter."""

from __future__ import annotations

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import (
    colored,
    feature_header,
    failures_block,
    progress_bar,
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

    def _print(self, text: str) -> None:
        if not self._printed_header:
            self._printed_header = True
            self._print_header()
        self._stream.write(text + "\n")
        self._stream.flush()

    def _print_header(self) -> None:
        self._stream.write(colored("\n🚀 Behave Modern Console Report\n", "bold", self.formatter_config.colors))
        total = self._collector.execution.total_scenarios
        self._stream.write(f"Running {total} scenarios...\n")
        self._stream.flush()

    def on_result(self) -> None:
        """Print newly completed scenarios and steps as they finish."""
        cfg = self.formatter_config
        for feature in self._collector.execution.features:
            feature_id = id(feature)
            if feature_id not in self._printed_features:
                self._print(feature_header(feature, cfg.colors))
                self._printed_features.add(feature_id)

            for scenario in feature.scenarios:
                if scenario.is_terminal and id(scenario) not in self._printed_scenarios:
                    self._print(scenario_line(scenario, colors=cfg.colors))
                    if cfg.show_steps:
                        for step in scenario.steps:
                            self._print(step_line(step, colors=cfg.colors))
                            if step.is_failed and step.error and cfg.show_traceback:
                                self._print(f"      {step.error.message}")
                                if step.error.traceback:
                                    for tb_line in step.error.traceback.splitlines():
                                        self._print(f"      {tb_line}")
                    self._printed_scenarios.add(id(scenario))

    def on_close(self) -> None:
        """Print progress bar, summary, and failures at the end."""
        cfg = self.formatter_config
        # Ensure all completed scenarios are printed before the final blocks.
        self.on_result()
        # Print any scenarios that were not emitted earlier (e.g. skipped).
        for feature in self._collector.execution.features:
            if id(feature) not in self._printed_features:
                self._print(feature_header(feature, cfg.colors))
                self._printed_features.add(id(feature))
            for scenario in feature.scenarios:
                if id(scenario) not in self._printed_scenarios:
                    self._print(scenario_line(scenario, colors=cfg.colors))
                    if cfg.show_steps:
                        for step in scenario.steps:
                            self._print(step_line(step, colors=cfg.colors))
                            if step.is_failed and step.error and cfg.show_traceback:
                                self._print(f"      {step.error.message}")
                                if step.error.traceback:
                                    for tb_line in step.error.traceback.splitlines():
                                        self._print(f"      {tb_line}")
                    self._printed_scenarios.add(id(scenario))
        if cfg.show_progress:
            self._print(progress_bar(self._collector.execution, colors=cfg.colors))
        self._print(summary_block(self._collector.execution, colors=cfg.colors))
        if cfg.show_traceback:
            failures = failures_block(self._collector.execution, colors=cfg.colors)
            if failures:
                self._print(failures)
