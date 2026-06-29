"""Tests for statistics helpers."""

from behave_modern_console_report.models import Execution, Feature, Scenario, Status, Step
from behave_modern_console_report.statistics import (
    count_steps,
    failed_scenarios,
    recompute_execution,
    total_steps,
)


def test_recompute_execution_counts() -> None:
    execution = Execution(
        features=[
            Feature(
                scenarios=[
                    Scenario(
                        steps=[Step(status=Status.PASSED)],
                        status=Status.PASSED,
                    ),
                    Scenario(
                        steps=[Step(status=Status.FAILED)],
                        status=Status.FAILED,
                    ),
                ]
            )
        ]
    )
    recompute_execution(execution)
    assert execution.total_scenarios == 2
    assert execution.completed_scenarios == 2
    assert execution.passed_scenarios == 1
    assert execution.failed_scenarios == 1


def test_count_steps() -> None:
    scenario = Scenario(
        steps=[
            Step(status=Status.PASSED),
            Step(status=Status.FAILED),
            Step(status=Status.SKIPPED),
        ]
    )
    counts = count_steps(scenario)
    assert counts[Status.PASSED] == 1
    assert counts[Status.FAILED] == 1
    assert counts[Status.SKIPPED] == 1


def test_total_steps() -> None:
    execution = Execution(
        features=[
            Feature(
                scenarios=[
                    Scenario(steps=[Step(), Step()]),
                    Scenario(steps=[Step()]),
                ]
            )
        ]
    )
    assert total_steps(execution) == 3


def test_failed_scenarios_pairs() -> None:
    feature = Feature(name="F1", scenarios=[Scenario(name="S1", status=Status.FAILED)])
    execution = Execution(features=[feature])
    pairs = failed_scenarios(execution)
    assert len(pairs) == 1
    assert pairs[0][0].name == "F1"
    assert pairs[0][1].name == "S1"
