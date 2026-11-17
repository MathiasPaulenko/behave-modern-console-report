"""Tests for the event collector."""

from behave_modern_console_report.collector import Collector, _extract_error
from behave_modern_console_report.config import FormatterConfig
from behave_modern_console_report.models import Status
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
    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    assert collector._current_step.status == Status.RUNNING
    assert collector._current_scenario.status == Status.RUNNING


def test_update_result_passed() -> None:
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
    step = FakeStep(status="failed", error_message="")
    error = _extract_error(step)
    assert error.type == ""
    assert error.message == ""


def test_extract_error_single_line_no_colon() -> None:
    """_extract_error with a single line and no colon should use it as message."""
    step = FakeStep(status="failed", error_message="Something went wrong")
    error = _extract_error(step)
    assert error.type == ""
    assert error.message == "Something went wrong"


def test_extract_error_multiline_no_colon() -> None:
    """_extract_error with multiline and no colon on first line."""
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

    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep(status="skipped"))
    # Simulate incorrect RUNNING state (e.g. from a previous set_running call)
    collector._current_scenario.status = Status.RUNNING
    # update_result should recalculate and fix the status
    collector.update_result(FakeStep(status="skipped"))
    assert collector._current_scenario.status == Status.SKIPPED


def test_update_result_error_status_counts_as_failed() -> None:
    """Regression: a step raising a non-AssertionError (behave Status.error)
    must count the scenario as failed, not skipped."""
    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    collector.update_result(
        FakeStep(
            status="error",
            duration=0.1,
            error_message="ERROR: ValueError: kaboom",
            exception=ValueError("kaboom"),
        )
    )
    assert collector._current_step.status == Status.FAILED
    assert collector._current_scenario.status == Status.FAILED
    assert collector.execution.failed_scenarios == 1
    assert collector.execution.skipped_scenarios == 0


def test_finish_syncs_silently_skipped_steps() -> None:
    """Regression: steps marked skipped after a failure emit no result().

    Behave assigns step.status=skipped without notifying the formatter, so
    the internal steps stay UNTESTED. finish() must re-read behave statuses
    so rendered icons are truthful.
    """
    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    behave_step_1 = FakeStep()
    behave_step_2 = FakeStep()
    collector.add_step(behave_step_1)
    collector.add_step(behave_step_2)
    collector.set_running(FakeMatch())
    collector.update_result(
        FakeStep(status="failed", duration=0.1, error_message="AssertionError: nope")
    )
    # Behave marks the remaining step skipped without a result() event.
    behave_step_2.status = "skipped"
    scenario = collector._current_scenario
    assert scenario.status == Status.FAILED
    assert scenario.steps[1].status == Status.UNTESTED  # stale until finish

    collector.finish()
    assert scenario.steps[1].status == Status.SKIPPED


def test_finish_upgrades_late_hook_failure() -> None:
    """Regression: a scenario counted PASSED can still fail afterwards when an
    after_scenario hook or context cleanup raises. finish() must recount it
    as failed."""
    collector = make_collector()
    collector.add_feature(FakeFeature())
    behave_scenario = FakeScenario(status="untested")
    collector.add_scenario(behave_scenario)
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    collector.update_result(FakeStep(status="passed", duration=0.1))
    assert collector.execution.passed_scenarios == 1

    # The hook fails after the scenario was already counted.
    behave_scenario.status = "hook_error"
    collector.finish()
    assert collector._current_scenario.status == Status.FAILED
    assert collector.execution.passed_scenarios == 0
    assert collector.execution.failed_scenarios == 1


def test_finish_marks_mid_run_skip_as_skipped() -> None:
    """Regression: scenario.skip() after passing steps makes Behave report the
    scenario as skipped; finish() must reconcile the stale PASSED count."""
    collector = make_collector()
    collector.add_feature(FakeFeature())
    behave_scenario = FakeScenario(status="untested")
    collector.add_scenario(behave_scenario)
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    collector.update_result(FakeStep(status="passed", duration=0.1))
    assert collector.execution.passed_scenarios == 1

    behave_scenario.status = "skipped"
    collector.finish()
    assert collector._current_scenario.status == Status.SKIPPED
    assert collector.execution.passed_scenarios == 0
    assert collector.execution.skipped_scenarios == 1


def test_finish_keeps_undefined_over_behave_error() -> None:
    """A scenario with an undefined step stays UNDEFINED even though Behave
    reports the scenario status as 'error' (it folds undefined into error)."""
    collector = make_collector()
    collector.add_feature(FakeFeature())
    behave_scenario = FakeScenario(status="error")
    collector.add_scenario(behave_scenario)
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    collector.update_result(FakeStep(status="undefined", duration=0.1))
    collector.finish()
    assert collector._current_scenario.status == Status.UNDEFINED
    assert collector.execution.undefined_scenarios == 1
    assert collector.execution.failed_scenarios == 0


def test_update_result_matches_by_step_identity() -> None:
    """Regression: a result must update its own step even when an earlier step
    is still non-terminal (e.g. dry-run results that stay untested)."""
    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    behave_step_1 = FakeStep()
    behave_step_2 = FakeStep()
    collector.add_step(behave_step_1)
    collector.add_step(behave_step_2)

    # Dry-run emulation: step 1 result stays untested; step 2 result must NOT
    # be applied to step 1 again.
    behave_step_1.status = "untested"
    collector.update_result(behave_step_1)
    behave_step_2.status = "undefined"
    collector.update_result(behave_step_2)

    steps = collector._current_scenario.steps
    assert steps[0].status == Status.UNTESTED
    assert steps[1].status == Status.UNDEFINED
    assert collector._current_scenario.status == Status.UNDEFINED


def test_update_result_for_unknown_step_creates_step() -> None:
    """A result for a step never announced via step() must not be dropped."""
    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep(status="skipped"))
    # All known steps are terminal; a result arrives for an unknown step.
    collector.update_result(FakeStep(name="mystery step", status="passed", duration=0.1))
    steps = collector._current_scenario.steps
    assert len(steps) == 2
    assert steps[1].name == "mystery step"
    assert steps[1].status == Status.PASSED


def test_scenario_without_feature_is_counted() -> None:
    """Regression: a scenario event with no prior feature must not make
    completed < total forever."""
    collector = make_collector()
    behave_scenario = FakeScenario(status="untested")
    collector.add_scenario(behave_scenario)  # no add_feature call
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    collector.update_result(FakeStep(status="passed", duration=0.1))
    collector.finish()
    assert collector.execution.completed_scenarios == 1
    assert collector.execution.passed_scenarios == 1
    assert collector.execution.completion_rate == 1.0


def test_finish_recomputes_feature_duration() -> None:
    """Feature.duration aggregates leftover scenario durations at finish."""
    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario(status="untested"))
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    collector.update_result(FakeStep(status="passed", duration=2.5))
    collector.finish()
    assert collector.execution.features[0].duration == 2.5


def test_extract_error_traceback_first_line_not_a_type() -> None:
    """Regression: 'Traceback (most recent call last):' must not be parsed as
    an error type."""
    step = FakeStep(
        status="failed",
        error_message='Traceback (most recent call last):\n  File "x.py"',
    )
    error = _extract_error(step)
    assert error.type == ""
    assert error.message == "Traceback (most recent call last):"


def test_extract_error_non_string_error_message() -> None:
    """_extract_error must survive a non-string error_message."""
    step = FakeStep(status="failed", error_message=123)  # type: ignore[arg-type]
    error = _extract_error(step)
    assert error.type == ""
    assert error.message == "123"


def test_update_result_non_numeric_duration() -> None:
    """Regression: a non-numeric step duration must not break aggregation."""
    collector = make_collector()
    collector.add_feature(FakeFeature())
    collector.add_scenario(FakeScenario())
    collector.add_step(FakeStep())
    collector.set_running(FakeMatch())
    result = FakeStep(status="passed")
    result.duration = "not-a-number"  # type: ignore[assignment]
    collector.update_result(result)
    assert collector._current_step.duration == 0.0
    assert collector._current_scenario.duration == 0.0


def test_add_step_without_scenario_is_ignored() -> None:
    """A step event with no active scenario must not crash or leak state."""
    collector = make_collector()
    collector.add_step(FakeStep())
    assert collector._current_scenario is None
    assert collector.execution.total_scenarios == 0


def test_update_result_without_scenario_does_not_crash() -> None:
    """A result event with no active scenario is safely dropped."""
    collector = make_collector()
    collector.update_result(FakeStep(status="passed"))
    assert collector.execution.total_scenarios == 0
    assert collector.execution.completed_scenarios == 0


def test_tag_name_handles_plain_strings() -> None:
    """Tags may be plain strings rather than objects with .name."""
    collector = make_collector()
    feature = FakeFeature()
    feature.tags = ["fast", "regression"]  # type: ignore[list-item]
    collector.add_feature(feature)
    assert collector.execution.features[0].tags == ["fast", "regression"]
