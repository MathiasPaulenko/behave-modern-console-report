"""Shared test fixtures and helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from behave_modern_console_report.config import Config, Verbosity
from behave_modern_console_report.themes import Theme, ThemeName, get_theme


@dataclass
class FakeTag:
    """Minimal Behave tag stand-in."""

    name: str


@dataclass
class FakeFeature:
    """Minimal Behave feature stand-in."""

    name: str = "Feature"
    description: list[str] = field(default_factory=list)
    tags: list[FakeTag] = field(default_factory=list)
    line: int = 1


@dataclass
class FakeScenario:
    """Minimal Behave scenario stand-in."""

    name: str = "Scenario"
    tags: list[FakeTag] = field(default_factory=list)
    line: int = 2


@dataclass
class FakeStep:
    """Minimal Behave step stand-in."""

    name: str = "step"
    keyword: str = "Given"
    line: int = 3
    status: str = "untested"
    duration: float = 0.0
    error_message: str = ""
    exception: BaseException | None = None


@dataclass
class FakeMatch:
    """Minimal Behave match stand-in."""

    location: str = ""
    arguments: list[Any] = field(default_factory=list)


class FakeBehaveConfig:
    """Minimal Behave configuration stand-in."""

    def __init__(self, user_data: dict[str, str] | None = None) -> None:
        self.userdata = user_data or {}


@pytest.fixture
def fake_config() -> FakeBehaveConfig:
    """Return a default fake Behave config."""
    return FakeBehaveConfig()


@pytest.fixture
def minimal_config() -> Config:
    """Return a minimal Config for testing."""
    return Config(
        theme=ThemeName.MINIMAL,
        verbosity=Verbosity.NORMAL,
        colors=False,
        compact=False,
        show_steps=False,
        show_steps_auto=False,
        show_durations=True,
        show_progress=True,
        show_environment=False,
        show_traceback=True,
        is_ci=False,
        is_interactive=False,
    )


@pytest.fixture
def default_theme() -> Theme:
    """Return the default theme."""
    return get_theme(ThemeName.DEFAULT)
