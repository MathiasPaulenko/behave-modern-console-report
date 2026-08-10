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
    assert Status.from_behave("running") == Status.RUNNING
    assert Status.from_behave("unknown") == Status.UNTESTED


def test_status_from_behave_none() -> None:
    """Regression: Status.from_behave must handle None without crashing."""
    assert Status.from_behave(None) == Status.UNTESTED


def test_status_from_behave_empty_string() -> None:
    """Status.from_behave must handle empty string without crashing."""
    assert Status.from_behave("") == Status.UNTESTED


def test_status_from_behave_non_string_name() -> None:
    """Status.from_behave must handle objects with non-string .name attribute."""

    class FakeStatus:
        name = 123

    assert Status.from_behave(FakeStatus()) == Status.UNTESTED


def test_status_from_behave_enum_like_object() -> None:
    """Status.from_behave should work with enum-like objects that have a .name."""

    class FakeStatus:
        name = "passed"

    assert Status.from_behave(FakeStatus()) == Status.PASSED


def test_scenario_update_status_passed() -> None:
    scenario = Scenario(steps=[Step(status=Status.PASSED), Step(status=Status.PASSED)])
    scenario.update_status()
    assert scenario.status == Status.PASSED


def test_scenario_update_status_failed() -> None:
    scenario = Scenario(steps=[Step(status=Status.PASSED), Step(status=Status.FAILED)])
    scenario.update_status()
    assert scenario.status == Status.FAILED


def test_scenario_update_status_skipped() -> None:
    scenario = Scenario(steps=[Step(status=Status.SKIPPED), Step(status=Status.SKIPPED)])
    scenario.update_status()
    assert scenario.status == Status.SKIPPED


def test_scenario_update_status_running() -> None:
    scenario = Scenario(steps=[Step(status=Status.PASSED), Step(status=Status.RUNNING)])
    scenario.update_status()
    assert scenario.status == Status.RUNNING


def test_scenario_update_status_mixed_passed_skipped() -> None:
    """Regression: mixed PASSED+SKIPPED steps should yield PASSED, not UNTESTED."""
    scenario = Scenario(steps=[Step(status=Status.PASSED), Step(status=Status.SKIPPED)])
    scenario.update_status()
    assert scenario.status == Status.PASSED


def test_scenario_update_status_undefined_takes_priority_over_skipped() -> None:
    scenario = Scenario(steps=[Step(status=Status.SKIPPED), Step(status=Status.UNDEFINED)])
    scenario.update_status()
    assert scenario.status == Status.UNDEFINED


def test_scenario_update_status_pending_takes_priority_over_skipped() -> None:
    scenario = Scenario(steps=[Step(status=Status.SKIPPED), Step(status=Status.PENDING)])
    scenario.update_status()
    assert scenario.status == Status.PENDING


def test_scenario_update_status_mixed_terminal_and_untested() -> None:
    """Regression: mixed terminal+UNTESTED steps should yield RUNNING, not UNTESTED."""
    scenario = Scenario(steps=[Step(status=Status.PASSED), Step(status=Status.UNTESTED)])
    scenario.update_status()
    assert scenario.status == Status.RUNNING


def test_scenario_update_status_mixed_skipped_and_untested() -> None:
    """Regression: mixed SKIPPED+UNTESTED steps should yield RUNNING, not UNTESTED."""
    scenario = Scenario(steps=[Step(status=Status.SKIPPED), Step(status=Status.UNTESTED)])
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


def test_feature_update_status_mixed_passed_skipped() -> None:
    """Regression: mixed PASSED+SKIPPED scenarios should yield PASSED, not UNTESTED."""
    feature = Feature(
        scenarios=[
            Scenario(status=Status.PASSED),
            Scenario(status=Status.SKIPPED),
        ]
    )
    feature.update_status()
    assert feature.status == Status.PASSED


def test_feature_update_status_pending() -> None:
    """Regression: Feature.update_status() was missing PENDING check."""
    feature = Feature(
        scenarios=[
            Scenario(status=Status.PASSED),
            Scenario(status=Status.PENDING),
        ]
    )
    feature.update_status()
    assert feature.status == Status.PENDING


def test_feature_update_status_mixed_terminal_and_untested() -> None:
    """Regression: mixed terminal+UNTESTED scenarios should yield RUNNING, not UNTESTED."""
    feature = Feature(
        scenarios=[
            Scenario(status=Status.PASSED),
            Scenario(status=Status.UNTESTED),
        ]
    )
    feature.update_status()
    assert feature.status == Status.RUNNING


def test_feature_update_status_running() -> None:
    """Regression: Feature.update_status() was missing RUNNING check."""
    feature = Feature(
        scenarios=[
            Scenario(status=Status.PASSED),
            Scenario(status=Status.RUNNING),
        ]
    )
    feature.update_status()
    assert feature.status == Status.RUNNING


def test_feature_update_status_undefined() -> None:
    feature = Feature(
        scenarios=[
            Scenario(status=Status.PASSED),
            Scenario(status=Status.UNDEFINED),
        ]
    )
    feature.update_status()
    assert feature.status == Status.UNDEFINED


def test_feature_update_status_all_skipped() -> None:
    feature = Feature(
        scenarios=[
            Scenario(status=Status.SKIPPED),
            Scenario(status=Status.SKIPPED),
        ]
    )
    feature.update_status()
    assert feature.status == Status.SKIPPED


def test_execution_add_scenario_result() -> None:
    execution = Execution()
    execution.add_scenario_result(Status.PASSED)
    execution.add_scenario_result(Status.FAILED)
    execution.add_scenario_result(Status.SKIPPED)
    assert execution.completed_scenarios == 3
    assert execution.passed_scenarios == 1
    assert execution.failed_scenarios == 1
    assert execution.skipped_scenarios == 1


def test_execution_add_scenario_result_undefined() -> None:
    """Regression: UNDEFINED scenarios were not counted in any category."""
    execution = Execution()
    execution.add_scenario_result(Status.PASSED)
    execution.add_scenario_result(Status.UNDEFINED)
    execution.add_scenario_result(Status.FAILED)
    assert execution.completed_scenarios == 3
    assert execution.passed_scenarios == 1
    assert execution.failed_scenarios == 1
    assert execution.undefined_scenarios == 1
    total_counted = (
        execution.passed_scenarios + execution.failed_scenarios + execution.undefined_scenarios
    )
    assert total_counted == 3


def test_execution_add_scenario_result_pending() -> None:
    """Regression: PENDING scenarios were not counted in any category."""
    execution = Execution()
    execution.add_scenario_result(Status.PASSED)
    execution.add_scenario_result(Status.PENDING)
    execution.add_scenario_result(Status.FAILED)
    assert execution.completed_scenarios == 3
    assert execution.passed_scenarios == 1
    assert execution.failed_scenarios == 1
    assert execution.pending_scenarios == 1
    total_counted = (
        execution.passed_scenarios
        + execution.failed_scenarios
        + execution.skipped_scenarios
        + execution.undefined_scenarios
        + execution.pending_scenarios
    )
    assert total_counted == 3


def test_execution_duration() -> None:
    execution = Execution(start_time=0.0, end_time=5.0)
    assert execution.duration == 5.0


def test_execution_duration_none_start() -> None:
    """Execution.duration with None start_time should return 0.0."""
    execution = Execution(start_time=None, end_time=5.0)
    assert execution.duration == 0.0


def test_execution_duration_none_end() -> None:
    """Execution.duration with None end_time should use start_time as end (duration 0)."""
    execution = Execution(start_time=5.0, end_time=None)
    assert execution.duration == 0.0


def test_execution_completion_rate_zero_total() -> None:
    """Execution.completion_rate with 0 total_scenarios should return 0.0."""
    execution = Execution()
    assert execution.completion_rate == 0.0


def test_execution_completion_rate_partial() -> None:
    """Execution.completion_rate should return correct fraction."""
    execution = Execution(total_scenarios=4)
    execution.add_scenario_result(Status.PASSED)
    execution.add_scenario_result(Status.FAILED)
    assert execution.completion_rate == 0.5


def test_error_summary() -> None:
    error = Error(type="AssertionError", message="Expected 200\nActual 500")
    assert error.summary == "AssertionError: Expected 200"


def test_error_summary_no_type() -> None:
    """Error.summary without type should return first line of message."""
    error = Error(message="Something went wrong\nLine 2")
    assert error.summary == "Something went wrong"


def test_error_summary_empty() -> None:
    """Error.summary with no type and no message should return 'Unknown error'."""
    error = Error()
    assert error.summary == "Unknown error"


def test_error_summary_type_empty_message() -> None:
    """Error.summary with type but empty message should return 'Type: '."""
    error = Error(type="ValueError", message="")
    assert error.summary == "ValueError: "
