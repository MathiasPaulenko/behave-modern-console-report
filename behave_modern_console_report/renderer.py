"""Render execution model into Rich terminal output.

The Renderer is independent from Behave. It receives the internal execution
model and produces Rich renderables. The Formatter decides whether to display
those renderables inside a live view or as discrete printed lines.
"""

from __future__ import annotations

from typing import Iterable

from rich.style import Style
from rich.text import Text

from behave_modern_console_report.config import Config, Verbosity
from behave_modern_console_report.icons import Icons
from behave_modern_console_report.models import Error, Execution, Feature, Scenario, Status, Step
from behave_modern_console_report.progress import ProgressBar
from behave_modern_console_report.statistics import failed_scenarios, recompute_execution
from behave_modern_console_report.themes import Theme
from behave_modern_console_report.utils import format_duration


class Renderer:
    """Convert an execution model into terminal renderables."""

    def __init__(self, config: Config, theme: Theme) -> None:
        self.config = config
        self.theme = theme
        self._header_rendered = False
        self._printed_ids: set[int] = set()
        self._progress_bar = ProgressBar(width=24, theme=theme)

    def render(self, execution: Execution, *, is_final: bool = False) -> Text:
        """Render the full output for the current execution state.

        Args:
            execution: Current execution model.
            is_final: When True, include summary and failure sections.

        Returns:
            A Rich renderable.
        """
        recompute_execution(execution)
        parts: list[RenderableType] = []

        if self.config.verbosity != Verbosity.MINIMAL:
            if self.config.is_interactive or not self._header_rendered:
                parts.append(self.render_header(execution))
                self._header_rendered = True

        if self.config.verbosity != Verbosity.MINIMAL:
            # In CI mode, scenarios are printed incrementally via next_ci_lines,
            # so the final render only needs to repeat them in interactive mode.
            if self.config.is_interactive or not is_final:
                parts.append(self._scenario_list(execution))
            if self.config.show_progress:
                parts.append(self.render_progress(execution))

        if is_final:
            parts.append(self.render_summary(execution))
            if self.config.verbosity != Verbosity.MINIMAL:
                parts.append(self.render_failures(execution))

        return Text("\n").join(parts) if parts else Text("")

    def render_header(self, execution: Execution) -> Text:
        """Render the report header."""
        title = Text(
            f"{Icons.RUNNING} Behave Modern Console Report",
            style=self.theme.header,
        )
        count = Text(
            f"Running {execution.total_scenarios} scenarios...",
            style=self.theme.muted,
        )
        return Text.assemble(title, Text("\n"), count)

    def render_progress(self, execution: Execution) -> Text:
        """Render the progress bar and scenario counts."""
        line = self._progress_bar.render_with_counts(execution)
        return Text.assemble(line, Text("\n"))

    def _scenario_list(self, execution: Execution) -> Text:
        """Render the list of recent scenarios grouped by feature."""
        scenarios = self._visible_scenarios(execution)
        if not scenarios:
            return Text("")

        lines: list[Text] = []
        current_feature: Feature | None = None
        for feature, scenario in scenarios:
            if feature is not current_feature:
                lines.append(Text(""))
                header = f"Feature: {feature.name or 'Unknown'}"
                lines.append(Text(header, style=self.theme.header))
                current_feature = feature
            lines.append(self._scenario_line(feature, scenario))
            if self.config.effective_show_steps():
                lines.extend(self._step_lines(scenario))

        return Text("\n").join(lines)

    def _visible_scenarios(self, execution: Execution) -> list[tuple[Feature, Scenario]]:
        """Return the scenarios that should be visible in the live list.

        In compact mode, only the most recently completed or running scenarios
        are shown. Otherwise, all scenarios with a non-untested status are shown.
        """
        all_scenarios: list[tuple[Feature, Scenario]] = []
        for feature in execution.features:
            for scenario in feature.scenarios:
                if scenario.status != Status.UNTESTED or feature.scenarios.index(scenario) == 0:
                    all_scenarios.append((feature, scenario))

        if self.config.compact:
            window_size = 10
            return all_scenarios[-window_size:] if all_scenarios else []
        return all_scenarios

    def _scenario_line(self, feature: Feature, scenario: Scenario) -> Text:
        """Render a single scenario status line."""
        icon = Icons.for_status(scenario.status)
        style = self._status_style(scenario.status)
        name = scenario.name or "Unnamed scenario"
        line = f"{icon} {name}"
        if self.config.show_durations and scenario.duration > 0:
            line += f"  ({format_duration(scenario.duration)})"
        return Text(line, style=style)

    def _step_lines(self, scenario: Scenario) -> list[Text]:
        """Render step-level lines for a scenario."""
        lines: list[Text] = []
        for step in scenario.steps:
            if step.status == Status.UNTESTED:
                continue
            icon = Icons.for_status(step.status)
            style = self._status_style(step.status)
            keyword = step.keyword or ""
            name = step.name or ""
            line = f"    {icon} {keyword} {name}".rstrip()
            if self.config.show_durations and step.duration > 0:
                line += f"  ({format_duration(step.duration)})"
            lines.append(Text(line, style=style))
        return lines

    def render_summary(self, execution: Execution) -> Text:
        """Render the final results summary."""
        recompute_execution(execution)
        lines = [
            Text("RESULTS", style=self.theme.header),
            Text(""),
            self._summary_line("Passed", execution.passed_scenarios, self.theme.passed),
            self._summary_line("Failed", execution.failed_scenarios, self.theme.failed),
            self._summary_line("Skipped", execution.skipped_scenarios, self.theme.skipped),
        ]
        if execution.undefined_scenarios:
            lines.append(
                self._summary_line(
                    "Undefined", execution.undefined_scenarios, self.theme.undefined
                )
            )
        if execution.pending_scenarios:
            lines.append(
                self._summary_line("Pending", execution.pending_scenarios, self.theme.pending)
            )
        lines.append(Text(""))
        lines.append(
            Text(
                f"{Icons.DURATION} Duration {format_duration(execution.duration)}",
                style=self.theme.duration,
            )
        )
        return Text("\n").join(lines)

    def _summary_line(self, label: str, value: int, style: Style) -> Text:
        """Render a single summary count line."""
        return Text.assemble(
            Text(f"{label:<9}", style=self.theme.text),
            Text(str(value), style=style),
        )

    def render_failures(self, execution: Execution) -> Text:
        """Render failure diagnostics."""
        failures = failed_scenarios(execution)
        if not failures:
            return Text("")

        parts: list[Text] = [Text("Failures", style=self.theme.failed)]
        for feature, scenario in failures:
            parts.append(self._failure_block(feature, scenario))
        return Text("\n").join(parts)

    def _failure_block(self, feature: Feature, scenario: Scenario) -> Text:
        """Render a single failure diagnostic block."""
        header = Text(
            f"{Icons.FAILED} {scenario.name or 'Unnamed scenario'}",
            style=self.theme.failed,
        )
        location = Text(
            f"  Feature: {feature.name or 'Unknown'} (line {scenario.line})",
            style=self.theme.muted,
        )
        lines: list[Text] = [header, location]

        error = self._first_error(scenario)
        if error:
            error_type = Text(error.type or "Error", style=self.theme.failed)
            lines.append(error_type)
            if error.message:
                lines.append(Text(error.message, style=self.theme.text))
            if self.config.show_traceback and error.traceback:
                traceback_text = Text(error.traceback, style=self.theme.muted)
                lines.append(traceback_text)

        return Text("\n").join(lines)

    def _first_error(self, scenario: Scenario) -> Error | None:
        """Return the first error attached to a scenario's steps."""
        for step in scenario.steps:
            if step.error is not None:
                return step.error
        return None

    def _status_style(self, status: Status) -> Style:
        """Return the theme style for a status."""
        mapping = {
            Status.PASSED: self.theme.passed,
            Status.FAILED: self.theme.failed,
            Status.SKIPPED: self.theme.skipped,
            Status.UNDEFINED: self.theme.undefined,
            Status.PENDING: self.theme.pending,
            Status.RUNNING: self.theme.running,
            Status.UNTESTED: self.theme.muted,
        }
        return mapping.get(status, self.theme.text)

    def next_ci_lines(self, execution: Execution) -> Iterable[Text]:
        """Yield scenario lines that have not yet been printed in CI mode.

        This allows the formatter to emit incremental log-friendly output.

        Args:
            execution: Current execution model.

        Yields:
            Text lines ready to be printed.
        """
        recompute_execution(execution)
        for feature in execution.features:
            for scenario in feature.scenarios:
                scenario_id = id(scenario)
                if scenario_id in self._printed_ids:
                    continue
                if scenario.status in {
                    Status.PASSED,
                    Status.FAILED,
                    Status.SKIPPED,
                    Status.UNDEFINED,
                    Status.PENDING,
                }:
                    self._printed_ids.add(scenario_id)
                    yield self._scenario_line(feature, scenario)
                    if self.config.effective_show_steps():
                        yield from self._step_lines(scenario)
