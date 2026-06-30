"""Shared test fixtures and helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest


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
