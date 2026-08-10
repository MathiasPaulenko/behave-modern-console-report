"""Tests for the event collector."""

from behave_modern_console_report.collector import Collector
from behave_modern_console_report.config import FormatterConfig
from tests.conftest import FakeBehaveConfig, FakeFeature, FakeMatch, FakeScenario, FakeStep


def make_collector() -> Collector:
    return Collector(FormatterConfig("modern", FakeBehaveConfig()))


def test_add_feature() -> None:
    collector = make_collector()
    collector.add_feature(FakeFeature(name="Login feature"))
    assert len(collector.execution.features) == 1
    assert collector.execution.features[0].name == "Login feature"


def test_add_scenario_increments_total() -> None:
    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario(name="Valid login"))
    collector.add_scenario(FakeScenario(name="Invalid login"))
    assert collector.execution.total_scenarios == 2


def test_add_step_attaches_to_scenario() -> None:
    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep(name="user enters credentials"))
    assert len(collector._current_scenario.steps) == 1
    assert collector._current_scenario.steps[0].name == "user enters credentials"


def test_set_running_marks_step() -> None:
    from behave_modern_console_report.models import Status
    from tests.conftest import FakeMatch

    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    assert collector._current_step.status == Status.RUNNING
    assert collector._current_scenario.status == Status.RUNNING


def test_update_result_passed() -> None:
    from behave_modern_console_report.models import Status

    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    collector.update_result(FakeStep(status="passed", duration=0.1))
    assert collector._current_step.status == Status.PASSED
    assert collector._current_scenario.status == Status.PASSED
    assert collector.execution.passed_scenarios == 1


def test_update_result_failed() -> None:
    from behave_modern_console_report.models import Status

    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    collector.update_result(
        FakeStep(
            status="failed",
            duration=0.2,
            error_message="AssertionError: expected 200",
        )
    )
    assert collector._current_step.status == Status.FAILED
    assert collector._current_scenario.status == Status.FAILED
    assert collector.execution.failed_scenarios == 1
    assert collector._current_step.error is not None
    assert collector._current_step.error.type == "AssertionError"


def test_add_feature_with_none_description() -> None:
    """Regression: Collector.add_feature must handle None description without crashing."""
    collector = make_collector()
    feature = FakeFeature(name="Test")
    feature.description = None  # type: ignore[assignment]
    collector.add_feature(feature)
    assert collector.execution.features[0].description == ""


def test_add_feature_with_none_tags() -> None:
    """Regression: Collector.add_feature must handle None tags without crashing."""
    collector = make_collector()
    feature = FakeFeature(name="Test")
    feature.tags = None  # type: ignore[assignment]
    collector.add_feature(feature)
    assert collector.execution.features[0].tags == []


def test_add_scenario_with_none_tags() -> None:
    """Regression: Collector.add_scenario must handle None tags without crashing."""
    collector = make_collector()
    collector.add_feature(FakeFeature())
    scenario = FakeScenario(name="Test")
    scenario.tags = None  # type: ignore[assignment]
    collector.add_scenario(scenario)
    assert collector._current_scenario is not None
    assert collector._current_scenario.tags == []


def test_update_result_undefined() -> None:
    """Regression: UNDEFINED scenarios must be counted in undefined_scenarios."""
    from behave_modern_console_report.models import Status

    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    collector.update_result(FakeStep(status="undefined", duration=0.1))
    assert collector._current_step.status == Status.UNDEFINED
    assert collector._current_scenario.status == Status.UNDEFINED
    assert collector.execution.undefined_scenarios == 1
    assert collector.execution.completed_scenarios == 1


def test_extract_error_with_exception() -> None:
    """_extract_error should use exception type name when exception is present."""
    from behave_modern_console_report.collector import _extract_error

    step = FakeStep(
        status="failed",
        error_message="Traceback here",
        exception=ValueError("bad value"),
    )
    error = _extract_error(step)
    assert error.type == "ValueError"
    assert error.message == "bad value"
    assert error.traceback == "Traceback here"


def test_extract_error_multiline_with_colon() -> None:
    """_extract_error should split type from message on first colon."""
    from behave_modern_console_report.collector import _extract_error

    step = FakeStep(
        status="failed",
        error_message="AssertionError: expected 200\nactual 500",
    )
    error = _extract_error(step)
    assert error.type == "AssertionError"
    assert error.message == "expected 200"
    assert error.traceback == "actual 500"


def test_update_result_exception_without_error_message() -> None:
    """Regression: error must be extracted when exception is set but error_message is empty."""
    from behave_modern_console_report.models import Status

    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    collector.update_result(
        FakeStep(
            status="failed",
            duration=0.2,
            error_message="",
            exception=ValueError("bad value"),
        )
    )
    assert collector._current_step.status == Status.FAILED
    assert collector._current_step.error is not None
    assert collector._current_step.error.type == "ValueError"
    assert collector._current_step.error.message == "bad value"


def test_extract_error_empty_message_no_exception() -> None:
    """_extract_error with empty message and no exception should return empty Error."""
    from behave_modern_console_report.collector import _extract_error

    step = FakeStep(status="failed", error_message="")
    error = _extract_error(step)
    assert error.type == ""
    assert error.message == ""


def test_extract_error_single_line_no_colon() -> None:
    """_extract_error with a single line and no colon should use it as message."""
    from behave_modern_console_report.collector import _extract_error

    step = FakeStep(status="failed", error_message="Something went wrong")
    error = _extract_error(step)
    assert error.type == ""
    assert error.message == "Something went wrong"


def test_extract_error_multiline_no_colon() -> None:
    """_extract_error with multiline and no colon on first line."""
    from behave_modern_console_report.collector import _extract_error

    step = FakeStep(
        status="failed",
        error_message="Something went wrong\nDetails here",
    )
    error = _extract_error(step)
    assert error.type == ""
    assert error.message == "Something went wrong"
    assert error.traceback == "Details here"


def test_set_running_no_non_terminal_step() -> None:
    """Regression: set_running() must NOT set scenario to RUNNING when all steps are terminal.

    This was the root cause of the 'Step is still running' bug. When a step is
    pre-terminal (e.g. skipped), Behave still calls match() and result() for it.
    set_running() would set the scenario to RUNNING, but update_result() couldn't
    find a non-terminal step to update, leaving the scenario stuck in RUNNING.
    """
    from behave_modern_console_report.models import Status

    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep(status="skipped"))
    # All steps are terminal (skipped). set_running should be a no-op.
    collector.set_running(FakeMatch())
    assert collector._current_scenario.status == Status.SKIPPED


def test_update_result_recovers_from_incorrect_running() -> None:
    """Regression: update_result() must recalculate scenario status even when
    no non-terminal step is found, to correct any incorrect RUNNING state."""
    from behave_modern_console_report.models import Status

    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep(status="skipped"))
    # Simulate incorrect RUNNING state (e.g. from a previous set_running call)
    collector._current_scenario.status = Status.RUNNING
    # update_result should recalculate and fix the status
    collector.update_result(FakeStep(status="skipped"))
    assert collector._current_scenario.status == Status.SKIPPED
