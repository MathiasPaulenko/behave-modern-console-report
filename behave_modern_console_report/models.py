"""Execution model dataclasses.

This module defines the internal execution model used by the formatter.
It is independent from Behave's own model objects so that rendering and
analysis can be tested without running Behave itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Status(Enum):
    """Execution status for features, scenarios, and steps."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    UNDEFINED = "undefined"
    PENDING = "pending"
    RUNNING = "running"
    UNTESTED = "untested"

    @classmethod
    def from_behave(cls, status: str) -> "Status":
        """Map a Behave status string to an internal Status value.

        Args:
            status: Behave status string, e.g. ``passed``, ``failed``.

        Returns:
            The corresponding internal Status value. Unknown values are mapped
            to ``UNTESTED``.
        """
        mapping = {
            "passed": cls.PASSED,
            "failed": cls.FAILED,
            "skipped": cls.SKIPPED,
            "undefined": cls.UNDEFINED,
            "pending": cls.PENDING,
            "executing": cls.RUNNING,
        }
        status_name = getattr(status, "name", str(status))
        return mapping.get(status_name.lower(), cls.UNTESTED)


@dataclass
class Error:
    """Error information attached to a failed step or scenario."""

    type: str = ""
    message: str = ""
    traceback: str = ""

    @property
    def summary(self) -> str:
        """Return a concise one-line error summary."""
        if self.type:
            return f"{self.type}: {self.message.splitlines()[0] if self.message else ''}"
        return self.message.splitlines()[0] if self.message else "Unknown error"


@dataclass
class Step:
    """A single step within a scenario."""

    name: str = ""
    keyword: str = ""
    status: Status = Status.UNTESTED
    duration: float = 0.0
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    error: Optional[Error] = None
    line: int = 0

    @property
    def is_terminal(self) -> bool:
        """Return True if the step has a final status."""
        return self.status in {
            Status.PASSED,
            Status.FAILED,
            Status.SKIPPED,
            Status.UNDEFINED,
            Status.PENDING,
        }

    @property
    def is_failed(self) -> bool:
        """Return True if the step failed."""
        return self.status == Status.FAILED


@dataclass
class Scenario:
    """A scenario (or scenario outline example) within a feature."""

    name: str = ""
    tags: list[str] = field(default_factory=list)
    status: Status = Status.UNTESTED
    duration: float = 0.0
    steps: list[Step] = field(default_factory=list)
    line: int = 0

    @property
    def is_failed(self) -> bool:
        """Return True if the scenario failed."""
        return self.status == Status.FAILED

    @property
    def is_terminal(self) -> bool:
        """Return True if the scenario has a final status."""
        return self.status in {
            Status.PASSED,
            Status.FAILED,
            Status.SKIPPED,
            Status.UNDEFINED,
            Status.PENDING,
        }

    @property
    def is_running(self) -> bool:
        """Return True if any step is currently running."""
        return any(step.status == Status.RUNNING for step in self.steps)

    def update_status(self) -> None:
        """Derive the scenario status from its steps."""
        if not self.steps:
            if not self.is_terminal:
                self.status = Status.UNTESTED
            return

        if any(step.status == Status.FAILED for step in self.steps):
            self.status = Status.FAILED
        elif any(step.status == Status.UNDEFINED for step in self.steps):
            self.status = Status.UNDEFINED
        elif any(step.status == Status.PENDING for step in self.steps):
            self.status = Status.PENDING
        elif all(step.status == Status.PASSED for step in self.steps):
            self.status = Status.PASSED
        elif all(step.status == Status.SKIPPED for step in self.steps):
            self.status = Status.SKIPPED
        elif any(step.status == Status.RUNNING for step in self.steps):
            self.status = Status.RUNNING
        else:
            self.status = Status.UNTESTED


@dataclass
class Feature:
    """A feature file containing scenarios."""

    name: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    status: Status = Status.UNTESTED
    duration: float = 0.0
    scenarios: list[Scenario] = field(default_factory=list)
    line: int = 0

    def update_status(self) -> None:
        """Derive the feature status from its scenarios."""
        if not self.scenarios:
            self.status = Status.UNTESTED
            return

        if any(scenario.status == Status.FAILED for scenario in self.scenarios):
            self.status = Status.FAILED
        elif any(scenario.status == Status.UNDEFINED for scenario in self.scenarios):
            self.status = Status.UNDEFINED
        elif all(scenario.status == Status.PASSED for scenario in self.scenarios):
            self.status = Status.PASSED
        elif all(scenario.status == Status.SKIPPED for scenario in self.scenarios):
            self.status = Status.SKIPPED
        else:
            self.status = Status.UNTESTED


@dataclass
class Environment:
    """Optional environment information captured at runtime."""

    python_version: str = ""
    platform: str = ""
    behave_version: str = ""
    user_data: dict[str, str] = field(default_factory=dict)


@dataclass
class Execution:
    """Root aggregate for a single Behave execution."""

    features: list[Feature] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_scenarios: int = 0
    completed_scenarios: int = 0
    passed_scenarios: int = 0
    failed_scenarios: int = 0
    skipped_scenarios: int = 0
    undefined_scenarios: int = 0
    pending_scenarios: int = 0
    environment: Environment = field(default_factory=Environment)
    errors: list[tuple[str, Error]] = field(default_factory=list)

    def add_scenario_result(self, status: Status) -> None:
        """Update aggregate counters when a scenario finishes."""
        self.completed_scenarios += 1
        if status == Status.PASSED:
            self.passed_scenarios += 1
        elif status == Status.FAILED:
            self.failed_scenarios += 1
        elif status == Status.SKIPPED:
            self.skipped_scenarios += 1
        elif status == Status.UNDEFINED:
            self.undefined_scenarios += 1
        elif status == Status.PENDING:
            self.pending_scenarios += 1

    @property
    def duration(self) -> float:
        """Return the total execution duration in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time is not None else self.start_time
        return end - self.start_time

    @property
    def pass_rate(self) -> float:
        """Return the pass rate as a fraction between 0 and 1."""
        if self.total_scenarios == 0:
            return 0.0
        return self.passed_scenarios / self.total_scenarios

    @property
    def completion_rate(self) -> float:
        """Return the completion rate as a fraction between 0 and 1."""
        if self.total_scenarios == 0:
            return 0.0
        return self.completed_scenarios / self.total_scenarios
