"""Tests for the event collector."""

from behave_modern_console_report.collector import Collector
from behave_modern_console_report.config import Config
from tests.conftest import FakeFeature, FakeMatch, FakeScenario, FakeStep


def make_collector() -> Collector:
    return Collector(Config())


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
