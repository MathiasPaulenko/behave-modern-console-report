"""Tests for progress bar rendering."""

from behave_modern_console_report.models import Execution
from behave_modern_console_report.progress import ProgressBar
from behave_modern_console_report.themes import get_theme, ThemeName


def test_progress_bar_zero_percent() -> None:
    execution = Execution(total_scenarios=10, completed_scenarios=0)
    bar = ProgressBar(width=10, theme=get_theme(ThemeName.DEFAULT))
    text = bar.render(execution)
    assert "0%" in text.plain
    assert "█" not in text.plain


def test_progress_bar_half_percent() -> None:
    execution = Execution(total_scenarios=10, completed_scenarios=5)
    bar = ProgressBar(width=10, theme=get_theme(ThemeName.DEFAULT))
    text = bar.render(execution)
    assert "50%" in text.plain


def test_progress_bar_with_counts() -> None:
    execution = Execution(total_scenarios=148, completed_scenarios=106)
    bar = ProgressBar(width=24, theme=get_theme(ThemeName.DEFAULT))
    text = bar.render_with_counts(execution)
    plain = text.plain
    assert "106 / 148 scenarios" in plain


def test_progress_bar_eta_appears_when_running() -> None:
    execution = Execution(
        start_time=0.0, total_scenarios=10, completed_scenarios=5
    )
    bar = ProgressBar(width=10, theme=get_theme(ThemeName.DEFAULT))
    text = bar.render_with_counts(execution)
    assert "ETA" in text.plain
