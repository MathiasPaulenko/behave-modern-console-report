"""Base formatter shared by all formatters in this package."""

from __future__ import annotations

from typing import Any

from behave.formatter.base import Formatter
from behave.model import Feature as BehaveFeature
from behave.model import Scenario as BehaveScenario
from behave.model import Step as BehaveStep

from behave_modern_console_report.collector import Collector
from behave_modern_console_report.config import FormatterConfig


class BaseFormatter(Formatter):
    """Shared base for all MCR formatters."""

    name: str = "base"
    description: str = "Shared base formatter"

    def __init__(self, stream: Any, config: Any) -> None:
        """Initialize the formatter with a stream and Behave configuration."""
        # Behave may pass a StreamOpener; unwrap the actual file for our own use.
        self._stream = getattr(stream, "stream", stream)
        super().__init__(stream, config)
        self.formatter_config = FormatterConfig(self.name, config)
        self._collector = Collector(self.formatter_config)
        self._closed = False

    def feature(self, feature: BehaveFeature) -> None:
        """Handle a Behave feature event."""
        self._collector.add_feature(feature)

    def scenario(self, scenario: BehaveScenario) -> None:
        """Handle a Behave scenario event."""
        self._collector.add_scenario(scenario)

    def step(self, step: BehaveStep) -> None:
        """Handle a Behave step event."""
        self._collector.add_step(step)

    def match(self, match: Any) -> None:
        """Handle a Behave step match event."""
        self._collector.set_running(match)

    def result(self, result: BehaveStep) -> None:
        """Handle a Behave step result event."""
        self._collector.update_result(result)
        self.on_result()

    def eof(self) -> None:
        """Handle end-of-feature event."""

    def close(self) -> None:
        """Finalize the report."""
        if self._closed:
            return
        self._closed = True
        self._collector.finish()
        self.on_close()

    def on_result(self) -> None:
        """Hook called after each step result. Override in subclasses."""

    def on_close(self) -> None:
        """Hook called once at the end of the execution. Override in subclasses."""
