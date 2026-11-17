"""Modern Playwright-like formatter."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rich.text import Text

from behave_modern_console_report.base import BaseFormatter
from behave_modern_console_report.render import (
    failures_block,
    feature_header,
    scenario_line,
    step_line,
    summary_block,
)

if TYPE_CHECKING:
    from behave_modern_console_report.models import Scenario


class ModernFormatter(BaseFormatter):
    """Playwright-like formatter with clean output and progress at the end."""

    name = "modern-console"
    description = "Playwright-like console report with feature grouping"

    def __init__(self, stream: Any, config: Any) -> None:
        super().__init__(stream, config)
        self._printed_features: set[int] = set()
        self._printed_scenarios: set[int] = set()
        self._printed_steps: set[int] = set()
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

    def _emit_scenario(self, scenario: Scenario, *, only_terminal: bool = True) -> None:
        """Print a scenario line and its steps (first time only)."""
        self._print(scenario_line(scenario))
        self._emit_steps(scenario, only_terminal=only_terminal)
        self._printed_scenarios.add(id(scenario))

    def _emit_steps(self, scenario: Scenario, *, only_terminal: bool = True) -> None:
        """Print step lines that have not been emitted yet.

        Steps Behave marks skipped after a failure get their status assigned
        without a ``result()`` event, so mid-run only terminal steps are
        emitted; leftovers are flushed when the run finishes.
        """
        cfg = self.formatter_config
        if not cfg.show_steps:
            return
        for step in scenario.steps:
            if id(step) in self._printed_steps:
                continue
            if only_terminal and not step.is_terminal:
                continue
            self._printed_steps.add(id(step))
            self._print(step_line(step))
            if step.is_failed and step.error and cfg.show_traceback:
                for message_line in step.error.message.splitlines() or [""]:
                    self._console.print(Text(f"      {message_line}", style="red"))
                if step.error.traceback:
                    for tb_line in step.error.traceback.splitlines():
                        self._console.print(Text(f"      {tb_line}", style="red"))

    def _emit_pending(self, *, final: bool = False) -> None:
        """Print all features/scenarios/steps that have not been emitted yet."""
        self._collector.sync_scenarios()
        for feature in self._collector.execution.features:
            has_pending = any(
                (id(scenario) not in self._printed_scenarios and scenario.is_terminal)
                or (
                    id(scenario) in self._printed_scenarios
                    and any(
                        id(step) not in self._printed_steps and (final or step.is_terminal)
                        for step in scenario.steps
                    )
                )
                for scenario in feature.scenarios
            )
            if has_pending and id(feature) not in self._printed_features:
                self._print(feature_header(feature))
                self._printed_features.add(id(feature))
            for scenario in feature.scenarios:
                if scenario.is_terminal and id(scenario) not in self._printed_scenarios:
                    self._emit_scenario(scenario, only_terminal=not final)
                elif id(scenario) in self._printed_scenarios:
                    self._emit_steps(scenario, only_terminal=not final)

    def on_result(self) -> None:
        """Print newly completed scenarios and steps as they finish."""
        self._emit_pending()

    def on_close(self) -> None:
        """Print progress bar, summary, and failures at the end."""
        cfg = self.formatter_config
        # Ensure all completed scenarios are printed before the final blocks.
        self._emit_pending(final=True)
        self._console.print(summary_block(self._collector.execution))
        if cfg.show_traceback:
            failures = failures_block(self._collector.execution)
            if failures:
                self._console.print(failures)
