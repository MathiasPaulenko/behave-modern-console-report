"""Tests for execution model dataclasses."""

from behave_modern_console_report.models import (
    Error,
    Execution,
    Feature,
    Scenario,
    Status,
    Step,
)


def test_status_from_behave_mapping() -> None:
    assert Status.from_behave("passed") == Status.PASSED
    assert Status.from_behave("failed") == Status.FAILED
    assert Status.from_behave("skipped") == Status.SKIPPED
    assert Status.from_behave("undefined") == Status.UNDEFINED
    assert Status.from_behave("pending") == Status.PENDING
    assert Status.from_behave("executing") == Status.RUNNING
    assert Status.from_behave("unknown") == Status.UNTESTED


def test_scenario_update_status_passed() -> None:
    scenario = Scenario(steps=[Step(status=Status.PASSED), Step(status=Status.PASSED)])
    scenario.update_status()
    assert scenario.status == Status.PASSED


def test_scenario_update_status_failed() -> None:
    scenario = Scenario(
        steps=[Step(status=Status.PASSED), Step(status=Status.FAILED)]
    )
    scenario.update_status()
    assert scenario.status == Status.FAILED


def test_scenario_update_status_skipped() -> None:
    scenario = Scenario(steps=[Step(status=Status.SKIPPED), Step(status=Status.SKIPPED)])
    scenario.update_status()
    assert scenario.status == Status.SKIPPED


def test_scenario_update_status_running() -> None:
    scenario = Scenario(
        steps=[Step(status=Status.PASSED), Step(status=Status.RUNNING)]
    )
    scenario.update_status()
    assert scenario.status == Status.RUNNING


def test_feature_update_status_aggregates_scenarios() -> None:
    feature = Feature(
        scenarios=[
            Scenario(status=Status.PASSED),
            Scenario(status=Status.FAILED),
        ]
    )
    feature.update_status()
    assert feature.status == Status.FAILED


def test_execution_add_scenario_result() -> None:
    execution = Execution()
    execution.add_scenario_result(Status.PASSED)
    execution.add_scenario_result(Status.FAILED)
    execution.add_scenario_result(Status.SKIPPED)
    assert execution.completed_scenarios == 3
    assert execution.passed_scenarios == 1
    assert execution.failed_scenarios == 1
    assert execution.skipped_scenarios == 1


def test_execution_duration() -> None:
    execution = Execution(start_time=0.0, end_time=5.0)
    assert execution.duration == 5.0


def test_execution_pass_rate() -> None:
    execution = Execution(total_scenarios=4, passed_scenarios=3)
    assert execution.pass_rate == 0.75


def test_error_summary() -> None:
    error = Error(type="AssertionError", message="Expected 200\nActual 500")
    assert error.summary == "AssertionError: Expected 200"
