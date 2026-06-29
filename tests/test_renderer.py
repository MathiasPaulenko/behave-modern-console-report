"""Tests for renderer output."""

from behave_modern_console_report.config import Config, Verbosity
from behave_modern_console_report.models import Error, Execution, Feature, Scenario, Status, Step
from behave_modern_console_report.renderer import Renderer
from behave_modern_console_report.themes import get_theme, ThemeName


def make_config(**kwargs) -> Config:
    defaults = {
        "theme": ThemeName.MINIMAL,
        "verbosity": Verbosity.NORMAL,
        "colors": False,
        "compact": False,
        "show_steps": False,
        "show_steps_auto": False,
        "show_durations": True,
        "show_progress": True,
        "show_environment": False,
        "show_traceback": True,
        "is_ci": False,
        "is_interactive": False,
    }
    defaults.update(kwargs)
    return Config(**defaults)


def test_render_header_contains_title() -> None:
    config = make_config()
    renderer = Renderer(config, get_theme(config.theme))
    execution = Execution(
        features=[
            Feature(
                scenarios=[
                    Scenario(name="S1", steps=[Step(status=Status.PASSED)]),
                    Scenario(name="S2", steps=[Step(status=Status.PASSED)]),
                ]
            )
        ]
    )
    output = renderer.render(execution)
    assert "Behave Modern Console Report" in output.plain
    assert "Running 2 scenarios" in output.plain


def test_render_summary_contains_counts() -> None:
    config = make_config()
    renderer = Renderer(config, get_theme(config.theme))
    execution = Execution(
        start_time=0.0,
        end_time=5.0,
        features=[
            Feature(
                scenarios=[
                    Scenario(name="S1", steps=[Step(status=Status.PASSED)]),
                    Scenario(name="S2", steps=[Step(status=Status.PASSED)]),
                    Scenario(name="S3", steps=[Step(status=Status.FAILED)]),
                ]
            )
        ],
    )
    output = renderer.render(execution, is_final=True)
    plain = output.plain
    assert "RESULTS" in plain
    assert "Passed   2" in plain
    assert "Failed   1" in plain
    assert "Duration" in plain


def test_render_failure_block_contains_scenario_name() -> None:
    config = make_config()
    renderer = Renderer(config, get_theme(config.theme))
    execution = Execution(
        features=[
            Feature(
                name="Checkout",
                scenarios=[
                    Scenario(
                        name="Payment fails",
                        status=Status.FAILED,
                        steps=[
                            Step(
                                status=Status.FAILED,
                                error=Error(
                                    type="AssertionError",
                                    message="Expected 200",
                                ),
                            )
                        ],
                    )
                ],
            )
        ]
    )
    output = renderer.render(execution, is_final=True)
    plain = output.plain
    assert "Payment fails" in plain
    assert "AssertionError" in plain
    assert "Expected 200" in plain


def test_render_minimal_only_summary() -> None:
    config = make_config(verbosity=Verbosity.MINIMAL)
    renderer = Renderer(config, get_theme(config.theme))
    execution = Execution(
        start_time=0.0,
        end_time=1.0,
        features=[Feature(scenarios=[Scenario(name="S1", steps=[Step(status=Status.PASSED)])])],
    )
    output = renderer.render(execution, is_final=True)
    plain = output.plain
    assert "RESULTS" in plain
    assert "Behave Modern Console Report" not in plain


def test_next_ci_lines_yields_completed_scenarios() -> None:
    config = make_config()
    renderer = Renderer(config, get_theme(config.theme))
    execution = Execution(
        features=[
            Feature(
                scenarios=[
                    Scenario(name="S1", steps=[Step(status=Status.PASSED)]),
                    Scenario(name="S2", steps=[Step(status=Status.FAILED)]),
                ]
            )
        ]
    )
    lines = list(renderer.next_ci_lines(execution))
    assert len(lines) == 2
    assert "S1" in lines[0].plain
    assert "S2" in lines[1].plain


def test_next_ci_lines_does_not_duplicate() -> None:
    config = make_config()
    renderer = Renderer(config, get_theme(config.theme))
    execution = Execution(
        features=[Feature(scenarios=[Scenario(name="S1", steps=[Step(status=Status.PASSED)])])]
    )
    first = list(renderer.next_ci_lines(execution))
    second = list(renderer.next_ci_lines(execution))
    assert len(first) == 1
    assert len(second) == 0
