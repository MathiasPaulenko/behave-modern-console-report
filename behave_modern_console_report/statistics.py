"""Execution statistics helpers.

The Collector is responsible for updating counters as events arrive. This
module provides additional read-only helpers for deriving summary statistics
from the execution model.
"""

from __future__ import annotations

from behave_modern_console_report.models import Execution, Feature, Scenario, Status


def recompute_execution(execution: Execution) -> None:
    """Recompute execution-level aggregates from the feature tree.

    Args:
        execution: Execution model to update in place.
    """
    execution.total_scenarios = 0
    execution.completed_scenarios = 0
    execution.passed_scenarios = 0
    execution.failed_scenarios = 0
    execution.skipped_scenarios = 0
    execution.undefined_scenarios = 0
    execution.pending_scenarios = 0

    for feature in execution.features:
        feature.update_status()
        for scenario in feature.scenarios:
            execution.total_scenarios += 1
            scenario.update_status()
            if scenario.is_terminal:
                execution.completed_scenarios += 1
            if scenario.status == Status.PASSED:
                execution.passed_scenarios += 1
            elif scenario.status == Status.FAILED:
                execution.failed_scenarios += 1
            elif scenario.status == Status.SKIPPED:
                execution.skipped_scenarios += 1
            elif scenario.status == Status.UNDEFINED:
                execution.undefined_scenarios += 1
            elif scenario.status == Status.PENDING:
                execution.pending_scenarios += 1

        feature.duration = sum(
            scenario.duration for scenario in feature.scenarios if scenario.duration
        )


def count_steps(scenario: Scenario) -> dict[Status, int]:
    """Count steps by status within a scenario.

    Args:
        scenario: Scenario model.

    Returns:
        Mapping from Status to count.
    """
    counts: dict[Status, int] = {
        Status.PASSED: 0,
        Status.FAILED: 0,
        Status.SKIPPED: 0,
        Status.UNDEFINED: 0,
        Status.PENDING: 0,
        Status.RUNNING: 0,
        Status.UNTESTED: 0,
    }
    for step in scenario.steps:
        counts[step.status] = counts.get(step.status, 0) + 1
    return counts


def total_steps(execution: Execution) -> int:
    """Return the total number of steps across all scenarios."""
    return sum(
        len(scenario.steps)
        for feature in execution.features
        for scenario in feature.scenarios
    )


def failed_scenarios(execution: Execution) -> list[tuple[Feature, Scenario]]:
    """Return all failed scenarios paired with their parent feature."""
    result: list[tuple[Feature, Scenario]] = []
    for feature in execution.features:
        for scenario in feature.scenarios:
            if scenario.status == Status.FAILED:
                result.append((feature, scenario))
    return result
