"""Collect Behave events and build the internal execution model."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from behave_modern_console_report.models import Error, Execution, Feature, Scenario, Status, Step
from behave_modern_console_report.utils import now, sanitize_terminal_text

if TYPE_CHECKING:
    from behave.model import Feature as BehaveFeature
    from behave.model import Scenario as BehaveScenario
    from behave.model import Step as BehaveStep

    from behave_modern_console_report.config import FormatterConfig

_ERROR_TYPE_RE = re.compile(r"^[A-Za-z_][\w.]*$")


def _tag_name(tag: Any) -> str:
    """Return the tag name whether Behave provides a string or a Tag object."""
    name = getattr(tag, "name", None)
    return sanitize_terminal_text(name if name is not None else tag)


def _feature_description(feature: Any) -> str:
    """Return the feature description whether it is a list of lines or a string."""
    description = getattr(feature, "description", None)
    if not description:
        return ""
    if isinstance(description, str):
        return sanitize_terminal_text(description)
    return "\n".join(sanitize_terminal_text(line) for line in description)


class Collector:
    """Collects Behave events into an internal execution model."""

    def __init__(self, config: FormatterConfig) -> None:
        """Initialize the collector with formatter configuration."""
        self.config = config
        self.execution = Execution(start_time=now())
        self._current_feature: Feature | None = None
        self._current_scenario: Scenario | None = None
        self._current_step: Step | None = None
        self._all_scenarios: list[Scenario] = []
        self._completed_scenarios: set[int] = set()
        # Scenarios whose steps may still receive late statuses from Behave.
        # Bounds sync_scenarios() to O(dirty) instead of O(all scenarios).
        self._dirty_scenarios: set[int] = set()
        self._scenarios_by_id: dict[int, Scenario] = {}
        self._behave_scenarios: dict[int, BehaveScenario] = {}
        self._steps_by_behave_id: dict[int, Step] = {}
        self._behave_steps_by_internal_id: dict[int, BehaveStep] = {}

    def add_feature(self, feature: BehaveFeature) -> None:
        """Process a Behave feature event."""
        self._current_feature = Feature(
            name=sanitize_terminal_text(getattr(feature, "name", "") or ""),
            description=_feature_description(feature),
            tags=[_tag_name(tag) for tag in (getattr(feature, "tags", None) or [])],
            line=getattr(feature, "line", 0) or 0,
        )
        self.execution.features.append(self._current_feature)
        self._current_scenario = None
        self._current_step = None

    def add_scenario(self, scenario: BehaveScenario) -> None:
        """Process a Behave scenario event."""
        self._current_scenario = Scenario(
            name=sanitize_terminal_text(getattr(scenario, "name", "") or ""),
            tags=[_tag_name(tag) for tag in (getattr(scenario, "tags", None) or [])],
            line=getattr(scenario, "line", 0) or 0,
            status=Status.from_behave(getattr(scenario, "status", None)),
        )
        if self._current_feature is not None:
            self._current_feature.scenarios.append(self._current_scenario)
        self._all_scenarios.append(self._current_scenario)
        self._scenarios_by_id[id(self._current_scenario)] = self._current_scenario
        self._dirty_scenarios.add(id(self._current_scenario))
        self._behave_scenarios[id(self._current_scenario)] = scenario
        self.execution.total_scenarios += 1
        # Scenarios may already be terminal when added (e.g. tagged as @skip).
        if self._current_scenario.is_terminal:
            self._update_scenario()
        self._current_step = None

    def add_step(self, step: BehaveStep) -> None:
        """Process a Behave step event."""
        self._current_step = Step(
            name=sanitize_terminal_text(getattr(step, "name", "") or ""),
            keyword=sanitize_terminal_text(getattr(step, "keyword", "") or ""),
            line=getattr(step, "line", 0) or 0,
            status=Status.from_behave(getattr(step, "status", None)),
        )
        self._steps_by_behave_id[id(step)] = self._current_step
        self._behave_steps_by_internal_id[id(self._current_step)] = step
        if self._current_scenario is not None:
            self._current_scenario.steps.append(self._current_step)
            self._dirty_scenarios.add(id(self._current_scenario))
            # Skipped steps may already be terminal when added.
            if self._current_step.is_terminal:
                self._update_scenario()

    def set_running(self, _match: Any) -> None:
        """Mark the current step as running when Behave emits a match."""
        if self._current_scenario is not None:
            self._dirty_scenarios.add(id(self._current_scenario))
        target = self._find_non_terminal_step()  # First non-terminal step
        if target is not None:
            self._current_step = target
            self._current_step.status = Status.RUNNING
            if self._current_scenario is not None:
                self._current_scenario.status = Status.RUNNING

    def update_result(self, result: BehaveStep) -> None:
        """Update the step that matches the result from Behave."""
        if self._current_scenario is not None:
            self._dirty_scenarios.add(id(self._current_scenario))
        target = self._resolve_result_step(result)
        if target is not None:
            self._current_step = target
            target.status = Status.from_behave(getattr(result, "status", None))
            target.duration = _step_duration(result)
            if getattr(result, "error_message", "") or getattr(result, "exception", None):
                target.error = _extract_error(result)

        # Always recalculate scenario/feature status — even if no target was
        # found, the scenario may have been set to RUNNING by set_running()
        # and needs to be corrected based on actual step statuses.
        self._update_scenario()
        self._update_feature()

    def _resolve_result_step(self, result: BehaveStep) -> Step | None:
        """Find the internal step a Behave result belongs to.

        Behave passes the step object itself to ``result()``, so identity
        matching is exact whenever the step was announced via ``step()``.
        The first-non-terminal fallback covers results for steps that were
        never announced; if no step can take the result, a new one is created
        so the result is never dropped.
        """
        target = self._steps_by_behave_id.get(id(result))
        if target is not None:
            return target

        target = self._find_non_terminal_step()
        if target is None and self._current_scenario is not None:
            target = Step(
                name=sanitize_terminal_text(getattr(result, "name", "") or ""),
                keyword=sanitize_terminal_text(getattr(result, "keyword", "") or ""),
                line=getattr(result, "line", 0) or 0,
            )
            self._current_scenario.steps.append(target)
            self._steps_by_behave_id[id(result)] = target
            self._behave_steps_by_internal_id[id(target)] = result
        return target

    def _find_non_terminal_step(self) -> Step | None:
        """Return the first non-terminal step in the current scenario."""
        if self._current_scenario is None:
            return None
        for step in self._current_scenario.steps:
            if not step.is_terminal:
                return step
        return None

    def _sync_scenario_steps(self, scenario: Scenario) -> None:
        """Copy Behave statuses to steps that never produced a result event.

        Steps skipped or marked undefined after a failure get their status
        assigned by Behave without a ``result()`` call. Re-reading it here
        keeps the rendered icons truthful.
        """
        for step in scenario.steps:
            if step.is_terminal:
                continue
            behave_step = self._behave_steps_by_internal_id.get(id(step))
            if behave_step is None:
                continue
            step.status = Status.from_behave(getattr(behave_step, "status", None))

    def _update_scenario(self, scenario: Scenario | None = None) -> None:
        """Derive the scenario's status and update counters once it is terminal."""
        scenario = scenario or self._current_scenario
        if scenario is None:
            return

        self._sync_scenario_steps(scenario)
        scenario.update_status()
        scenario.duration = sum(step.duration for step in scenario.steps)

        scenario_id = id(scenario)
        if scenario.is_terminal and scenario_id not in self._completed_scenarios:
            self._completed_scenarios.add(scenario_id)
            self.execution.add_scenario_result(scenario.status)
        # A scenario can only keep changing while it or one of its steps is
        # still non-terminal; once fully settled it leaves the dirty set.
        if scenario.is_terminal and all(step.is_terminal for step in scenario.steps):
            self._dirty_scenarios.discard(scenario_id)

    def sync_scenarios(self) -> None:
        """Re-read Behave statuses for scenarios that may still change.

        Behave assigns ``skipped`` to remaining steps after a failure without
        emitting ``result()``, so statuses go stale until the next event.
        Called by formatters before emitting so late statuses are rendered
        correctly; counters are reconciled exactly once per scenario.
        """
        for scenario_id in tuple(self._dirty_scenarios):
            scenario = self._scenarios_by_id.get(scenario_id)
            if scenario is not None:
                self._update_scenario(scenario)

    def _update_feature(self) -> None:
        """Derive the current feature's status."""
        if self._current_feature is not None:
            self._current_feature.update_status()
            self._current_feature.duration = sum(
                scenario.duration for scenario in self._current_feature.scenarios
            )

    def finish(self) -> None:
        """Mark the execution as finished and reconcile all statuses.

        Steps skipped or marked undefined after a failure never emit
        ``result()``, and a scenario's Behave status can still change after
        its last counted result (hook failures, cleanup errors, mid-run
        ``scenario.skip()``). Behave's own status is the source of truth, so
        every scenario is reconciled against it and the aggregate counters
        are rebuilt from the final statuses.
        """
        self.execution.end_time = now()

        for scenario in self._all_scenarios:
            self._sync_scenario_steps(scenario)
            behave_scenario = self._behave_scenarios.get(id(scenario))
            final = Status.from_behave(getattr(behave_scenario, "status", None))
            if scenario.is_terminal:
                # UNDEFINED and PENDING stay as recorded — Behave folds them
                # into its generic "error" status and this model reports them
                # in their own summary buckets.
                if final == Status.FAILED and scenario.status not in (
                    Status.FAILED,
                    Status.UNDEFINED,
                    Status.PENDING,
                ):
                    scenario.status = Status.FAILED
                elif final == Status.SKIPPED and scenario.status == Status.PASSED:
                    scenario.status = Status.SKIPPED
            else:
                if not final.is_terminal:
                    # Never executed (or aborted mid-run): count as skipped so
                    # the scenario is not silently dropped from the summary.
                    final = Status.SKIPPED
                scenario.status = final
            scenario.duration = sum(step.duration for step in scenario.steps)
            # Everything is final now; keep _update_scenario from counting it
            # again if a late sync_scenarios() call reaches it.
            self._completed_scenarios.add(id(scenario))
        self._dirty_scenarios.clear()

        for feature in self.execution.features:
            feature.update_status()
            feature.duration = sum(scenario.duration for scenario in feature.scenarios)

        self.execution.recount(self._all_scenarios)


def _step_duration(result: Any) -> float:
    """Return the step duration, tolerating non-numeric values."""
    try:
        return float(getattr(result, "duration", 0.0) or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _extract_error(result: BehaveStep) -> Error:
    """Extract error information from a Behave step result."""
    error_message = sanitize_terminal_text(getattr(result, "error_message", "") or "")
    exception = getattr(result, "exception", None)

    if exception is not None:
        error_type = type(exception).__name__
        message = sanitize_terminal_text(str(exception))
        traceback = error_message
        return Error(type=error_type, message=message, traceback=traceback)

    lines = error_message.splitlines()
    if not lines:
        return Error(message=error_message)

    first_line = lines[0]
    if ":" in first_line and not first_line.startswith((" ", "\t")):
        error_type, _, message = first_line.partition(":")
        error_type = error_type.strip()
        # The "type" guess is only valid when it looks like an exception
        # name; lines like "Traceback (most recent call last):" are not one.
        if _ERROR_TYPE_RE.match(error_type):
            return Error(
                type=error_type,
                message=message.strip(),
                traceback="\n".join(lines[1:]).strip(),
            )

    return Error(message=first_line, traceback="\n".join(lines[1:]).strip())
