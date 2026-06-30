"""Collect Behave events and build the internal execution model."""

from __future__ import annotations

from typing import Any, Optional

from behave.model import Feature as BehaveFeature
from behave.model import Scenario as BehaveScenario
from behave.model import Step as BehaveStep

from behave_modern_console_report.config import FormatterConfig
from behave_modern_console_report.models import Error, Execution, Feature, Scenario, Status, Step
from behave_modern_console_report.utils import now


def _tag_name(tag: Any) -> str:
    """Return the tag name whether Behave provides a string or a Tag object."""
    return getattr(tag, "name", str(tag))


class Collector:
    """Collects Behave events into an internal execution model."""

    def __init__(self, config: FormatterConfig) -> None:
        """Initialize the collector with formatter configuration."""
        self.config = config
        self.execution = Execution(start_time=now())
        self._current_feature: Optional[Feature] = None
        self._current_scenario: Optional[Scenario] = None
        self._current_step: Optional[Step] = None
        self._completed_scenarios: set[int] = set()

    def add_feature(self, feature: BehaveFeature) -> None:
        """Process a Behave feature event."""
        self._current_feature = Feature(
            name=feature.name,
            description="\n".join(feature.description),
            tags=[_tag_name(tag) for tag in feature.tags],
            line=feature.line,
        )
        self.execution.features.append(self._current_feature)
        self._current_scenario = None
        self._current_step = None

    def add_scenario(self, scenario: BehaveScenario) -> None:
        """Process a Behave scenario event."""
        self._current_scenario = Scenario(
            name=scenario.name,
            tags=[_tag_name(tag) for tag in scenario.tags],
            line=scenario.line,
            status=Status.from_behave(getattr(scenario, "status", None)),
        )
        if self._current_feature is not None:
            self._current_feature.scenarios.append(self._current_scenario)
        self.execution.total_scenarios += 1
        # Scenarios may already be terminal when added (e.g. tagged as @skip).
        if self._current_scenario.is_terminal:
            self._update_scenario()
        self._current_step = None

    def add_step(self, step: BehaveStep) -> None:
        """Process a Behave step event."""
        self._current_step = Step(
            name=step.name,
            keyword=step.keyword,
            line=step.line,
            status=Status.from_behave(getattr(step, "status", None)),
        )
        if self._current_scenario is not None:
            self._current_scenario.steps.append(self._current_step)
            # Skipped steps may already be terminal when added.
            if self._current_step.is_terminal:
                self._update_scenario()

    def set_running(self, match: Any) -> None:
        """Mark the current step as running when Behave emits a match."""
        target = self._find_step_for_result(None)  # First non-terminal step
        if target is not None:
            self._current_step = target
            self._current_step.status = Status.RUNNING
        if self._current_scenario is not None:
            self._current_scenario.status = Status.RUNNING

    def update_result(self, result: BehaveStep) -> None:
        """Update the step that matches the result from Behave."""
        target = self._find_step_for_result(result)
        if target is None:
            return

        self._current_step = target
        self._current_step.status = Status.from_behave(result.status)
        self._current_step.duration = getattr(result, "duration", 0.0) or 0.0
        if result.error_message:
            self._current_step.error = _extract_error(result)

        self._update_scenario()
        self._update_feature()

    def _find_step_for_result(self, result: BehaveStep | None) -> Optional[Step]:
        """Return the first non-terminal step in the current scenario."""
        if self._current_scenario is None:
            return None
        for step in self._current_scenario.steps:
            if not step.is_terminal:
                return step
        return None

    def _update_scenario(self) -> None:
        """Derive the current scenario's status and update counters."""
        if self._current_scenario is None:
            return

        self._current_scenario.update_status()
        self._current_scenario.duration = sum(
            step.duration for step in self._current_scenario.steps
        )

        scenario_id = id(self._current_scenario)
        if self._current_scenario.is_terminal and scenario_id not in self._completed_scenarios:
            self._completed_scenarios.add(scenario_id)
            self.execution.add_scenario_result(self._current_scenario.status)

    def _update_feature(self) -> None:
        """Derive the current feature's status."""
        if self._current_feature is not None:
            self._current_feature.update_status()

    def finish(self) -> None:
        """Mark the execution as finished."""
        self.execution.end_time = now()


def _extract_error(result: BehaveStep) -> Error:
    """Extract error information from a Behave step result."""
    error_message = result.error_message or ""
    exception = getattr(result, "exception", None)

    if exception is not None:
        error_type = type(exception).__name__
        message = str(exception)
        traceback = error_message
        return Error(type=error_type, message=message, traceback=traceback)

    lines = error_message.splitlines()
    if not lines:
        return Error(message=error_message)

    first_line = lines[0]
    if ":" in first_line and not first_line.startswith(" "):
        error_type, _, message = first_line.partition(":")
        return Error(
            type=error_type.strip(),
            message=message.strip(),
            traceback="\n".join(lines[1:]).strip(),
        )

    return Error(message=first_line, traceback="\n".join(lines[1:]).strip())
